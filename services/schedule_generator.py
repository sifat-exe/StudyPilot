"""
schedule_generator.py
──────────────────────
Deterministic rule-based schedule generator and conflict resolver for StudyPilot.

Handles:
  1. Priority-weighted time allocation across courses.
  2. Class Routine conflict detection & avoidance (with correct slot parsing).
  3. Class Test (CT) time blocking per specific date.
  4. Interval merging for overlapping blocked periods (classes + CTs).
  5. Preferred study time window filtering (Morning, Afternoon, Evening, Any time).
  6. Daily study hour limits and buffer spacing.
  7. Session duration splitting (30, 45, 60, 90 mins).
  8. Final validation pass — rejects any session overlapping a blocked interval.
"""

from datetime import datetime, timedelta, time, date as date_type
from services.priority_calculator import calculate_priority


class ScheduleGenerator:
    """Generates a balanced study schedule based on user preferences and academic data."""

    TIME_WINDOWS = {
        "Morning": (8, 12),
        "Afternoon": (12, 17),
        "Evening": (17, 22),
        "Any time": (8, 22)
    }

    DAY_MAP = {
        0: "Monday",
        1: "Tuesday",
        2: "Wednesday",
        3: "Thursday",
        4: "Friday",
        5: "Saturday",
        6: "Sunday"
    }

    # Default CT duration to block when no end-time is available
    CT_DEFAULT_DURATION_MINS = 60

    def generate(
        self,
        courses: list,
        cts: list,
        assignments: list,
        routines: list,
        planning_period: str = "Next 7 days",
        hours_per_day: float = 3.0,
        session_length_mins: int = 60,
        preferred_time: str = "Any time"
    ) -> list:
        """
        Generates non-conflicting study sessions distributed across the planning period.

        Steps:
          1. Map CTs and assignments to courses for priority scoring.
          2. Compute session counts per course (priority-weighted).
          3. Parse Class Routine blocked intervals per weekday.
          4. Parse CT blocked intervals per specific date.
          5. Merge all blocked intervals per day.
          6. Generate candidate free-time slots using merged blocks.
          7. Distribute sessions across daily slots (round-robin by priority).
          8. Final validation — reject any session that overlaps a blocked interval.
        """
        if not courses:
            return []

        num_days = 1 if planning_period == "Today" else 7
        start_date = datetime.now().date()
        date_list = [start_date + timedelta(days=i) for i in range(num_days)]

        # ── 1. Map CTs and Assignments to Courses ────────────────────────────
        course_task_map = {}
        for c in courses:
            c_code = c["course_code"]
            c_cts = [item for item in cts if item["course_code"] == c_code]
            c_assigns = [
                item for item in assignments
                if item["course_code"] == c_code and not item.get("completed")
            ]

            highest_task = None
            session_type = "Revision"
            topic_desc = "General Study & Revision"

            if c_cts:
                sorted_cts = sorted(c_cts, key=lambda x: x["days_remaining"])
                highest_task = sorted_cts[0]
                session_type = "CT Preparation"
                topic_desc = highest_task.get("title", "CT Review")
            elif c_assigns:
                sorted_assigns = sorted(c_assigns, key=lambda x: x["days_remaining"])
                highest_task = sorted_assigns[0]
                session_type = "Assignment Work"
                topic_desc = highest_task.get("title", "Assignment")

            p_score = calculate_priority(highest_task, c)
            if p_score == 0:
                p_score = 10  # Minimum base priority for revision

            course_task_map[c["course_id"]] = {
                "course": c,
                "session_type": session_type,
                "topic_desc": topic_desc,
                "priority": p_score,
                "highest_task": highest_task
            }

        # ── 2. Total Study Time Allocation ───────────────────────────────────
        total_priority = sum(info["priority"] for info in course_task_map.values())
        if total_priority <= 0:
            total_priority = 1

        total_available_mins = num_days * hours_per_day * 60

        course_session_counts = {}
        for c_id, info in course_task_map.items():
            allocated_mins = (info["priority"] / total_priority) * total_available_mins
            num_sessions = max(1, round(allocated_mins / session_length_mins))
            course_session_counts[c_id] = num_sessions

        # ── 3. Parse Class Routine blocked intervals per weekday ──────────────
        routine_blocks = self._parse_routine_blocks(routines)

        # ── 4. Parse CT blocked intervals per specific date ───────────────────
        ct_blocks_by_date = self._parse_ct_blocks(cts, date_list)

        # ── 5. Pre-compute merged blocked intervals per date ──────────────────
        merged_blocks_by_date = {}
        for d in date_list:
            weekday_name = self.DAY_MAP[d.weekday()]
            routine_day = routine_blocks.get(weekday_name, [])
            ct_day = ct_blocks_by_date.get(d, [])
            all_blocks = routine_day + ct_day
            merged_blocks_by_date[d] = self._merge_intervals(all_blocks)

        # ── 6. Generate Candidate Free Time Slots per day ────────────────────
        window_start_h, window_end_h = self.TIME_WINDOWS.get(preferred_time, (8, 22))
        now = datetime.now()

        daily_slots = {}
        for d in date_list:
            merged_blocks = merged_blocks_by_date[d]
            slots = []

            window_start_dt = datetime.combine(d, time(window_start_h, 0))
            end_limit = datetime.combine(d, time(window_end_h, 0))

            # For today: never schedule a slot that has already started.
            if d == now.date():
                mins_past = now.minute % 15
                nudge = (15 - mins_past) if mins_past else 0
                earliest_start = now.replace(second=0, microsecond=0) + timedelta(minutes=nudge + 15)
                cur_time = max(window_start_dt, earliest_start)
            else:
                cur_time = window_start_dt

            max_mins_today = hours_per_day * 60
            mins_scheduled_today = 0

            while (
                cur_time + timedelta(minutes=session_length_mins) <= end_limit
                and mins_scheduled_today < max_mins_today
            ):
                slot_start = cur_time
                slot_end = cur_time + timedelta(minutes=session_length_mins)

                # Check conflict with merged blocked intervals
                conflict_end_dt = self._find_conflict_end(slot_start, slot_end, d, merged_blocks)

                if conflict_end_dt is None:
                    # No conflict — accept this slot
                    slots.append((slot_start, slot_end))
                    mins_scheduled_today += session_length_mins
                    cur_time = slot_end + timedelta(minutes=15)  # 15-min buffer
                else:
                    # Jump past the end of the conflicting blocked interval
                    cur_time = conflict_end_dt

            daily_slots[d] = slots

        # ── 7. Distribute Sessions (Balanced Round-Robin by Priority) ─────────
        session_pool = []
        for c_id, count in course_session_counts.items():
            session_pool.extend([c_id] * count)

        # Sort pool by priority descending so high-priority courses get first pick
        session_pool.sort(key=lambda cid: course_task_map[cid]["priority"], reverse=True)

        generated_sessions = []
        day_indices = {d: 0 for d in date_list}

        for c_id in session_pool:
            info = course_task_map[c_id]
            course = info["course"]

            # Find the day with fewest already-assigned sessions (spread evenly)
            sorted_days = sorted(
                date_list,
                key=lambda d: sum(1 for s in generated_sessions if s["date_obj"].date() == d)
            )

            assigned = False
            for d in sorted_days:
                idx = day_indices[d]
                slots_for_day = daily_slots[d]
                if idx < len(slots_for_day):
                    slot_start, slot_end = slots_for_day[idx]
                    day_indices[d] += 1

                    time_str = (
                        f"{d.strftime('%Y-%m-%d')} "
                        f"{slot_start.strftime('%I:%M %p')} - {slot_end.strftime('%I:%M %p')}"
                    )
                    task_str = f"{info['session_type']}: {course['course_code']} ({info['topic_desc']})"

                    generated_sessions.append({
                        "course_id": c_id,
                        "course_code": course["course_code"],
                        "course_title": course["course_title"],
                        "study_date": time_str,
                        "date_obj": slot_start,
                        "duration_minutes": session_length_mins,
                        "task": task_str,
                        "session_type": info["session_type"],
                        "priority": info["priority"],
                        "completed": 0
                    })
                    assigned = True
                    break

            if not assigned:
                # Fallback: try remaining days in reverse order
                for fallback_day in reversed(date_list):
                    idx = day_indices[fallback_day]
                    remaining_slots = daily_slots[fallback_day]
                    if idx < len(remaining_slots):
                        slot_start, slot_end = remaining_slots[idx]
                        day_indices[fallback_day] += 1

                        # Safety guard: never assign past slots on today
                        if slot_start <= now:
                            continue

                        time_str = (
                            f"{fallback_day.strftime('%Y-%m-%d')} "
                            f"{slot_start.strftime('%I:%M %p')} - {slot_end.strftime('%I:%M %p')}"
                        )
                        task_str = (
                            f"{info['session_type']}: {course['course_code']} ({info['topic_desc']})"
                        )
                        generated_sessions.append({
                            "course_id": c_id,
                            "course_code": course["course_code"],
                            "course_title": course["course_title"],
                            "study_date": time_str,
                            "date_obj": slot_start,
                            "duration_minutes": session_length_mins,
                            "task": task_str,
                            "session_type": info["session_type"],
                            "priority": info["priority"],
                            "completed": 0
                        })
                        break

        # ── 8. Final Validation Pass ─────────────────────────────────────────
        # Reject any session that — after all the above — still overlaps a blocked interval.
        validated_sessions = []
        for session in generated_sessions:
            s_start = session["date_obj"]
            s_end = s_start + timedelta(minutes=session["duration_minutes"])
            d = s_start.date()
            merged_blocks = merged_blocks_by_date.get(d, [])

            conflict = self._find_conflict_end(s_start, s_end, d, merged_blocks)
            if conflict is None:
                validated_sessions.append(session)
            # else: silently drop the conflicting session

        # Sort by date_obj ascending so the soonest session appears first
        validated_sessions.sort(key=lambda s: s["date_obj"])

        return validated_sessions

    # ── Helper: Parse Routine Blocks ─────────────────────────────────────────

    def _parse_routine_blocks(self, routines: list) -> dict:
        """
        Parses routine data into time-object intervals per day of week.

        The routine dict has:
          start_time = "9.40 AM - 10.30 AM"   (the slot label — contains BOTH start & end)
          end_time   = "Teacher: X | Room: Y | Slot: 9.40 AM - 10.30 AM"  (details, NOT a time)

        So we parse start/end from the start_time field by splitting on ' - '.
        Falls back to extracting the 'Slot:' portion from end_time if needed.
        """
        blocks = {}
        for r in routines:
            day = r.get("day_of_week", "").strip()
            slot_str = r.get("start_time", "").strip()  # e.g. "9.40 AM - 10.30 AM"

            t_start = None
            t_end = None

            if " - " in slot_str:
                parts = slot_str.split(" - ", 1)
                t_start = self._parse_time(parts[0].strip())
                t_end = self._parse_time(parts[1].strip())

            if not (t_start and t_end):
                # Fallback: try extracting from end_time's "Slot:" field
                end_field = r.get("end_time", "")
                if "Slot:" in end_field:
                    slot_part = end_field.split("Slot:", 1)[-1].strip()
                    if " - " in slot_part:
                        p = slot_part.split(" - ", 1)
                        t_start = self._parse_time(p[0].strip())
                        t_end = self._parse_time(p[1].strip())

            if t_start and t_end and day:
                blocks.setdefault(day, []).append((t_start, t_end))

        return blocks

    # ── Helper: Parse CT Blocks ──────────────────────────────────────────────

    def _parse_ct_blocks(self, cts: list, date_list: list) -> dict:
        """
        Parses CT data into time-object intervals per specific date.

        CT dict has date_str = "2026-10-04 8.00 AM" (date + time).
        We parse the time from the date_str. If no time component is found,
        we block a default duration (CT_DEFAULT_DURATION_MINS) from 08:00 AM.

        Returns: { date_object: [(time_start, time_end), ...], ... }
        Only includes dates that fall within date_list.
        """
        date_set = set(date_list)
        blocks = {}

        for ct in cts:
            date_str = ct.get("date_str", "").strip()
            if not date_str:
                continue

            ct_date = None
            ct_start_time = None

            # Try to parse "YYYY-MM-DD HH.MM AM/PM" or "YYYY-MM-DD HH:MM AM/PM"
            parts = date_str.split(" ", 1)
            try:
                ct_date = datetime.strptime(parts[0], "%Y-%m-%d").date()
            except ValueError:
                continue

            if len(parts) > 1:
                ct_start_time = self._parse_time(parts[1].strip())

            if ct_start_time is None:
                # No time in the date string — default to 08:00 AM
                ct_start_time = time(8, 0)

            # Compute end time
            start_dt = datetime.combine(ct_date, ct_start_time)
            end_dt = start_dt + timedelta(minutes=self.CT_DEFAULT_DURATION_MINS)
            ct_end_time = end_dt.time()

            # Only block dates within the planning window
            if ct_date in date_set:
                blocks.setdefault(ct_date, []).append((ct_start_time, ct_end_time))

        return blocks

    # ── Helper: Merge Overlapping Intervals ──────────────────────────────────

    def _merge_intervals(self, intervals: list) -> list:
        """
        Merges overlapping or adjacent (time, time) intervals.
        Input/output: list of (time_start, time_end) tuples.
        """
        if not intervals:
            return []

        # Convert time objects to comparable integers (minutes since midnight)
        def to_mins(t):
            return t.hour * 60 + t.minute

        def from_mins(m):
            return time(m // 60, m % 60)

        sorted_ivs = sorted(intervals, key=lambda x: to_mins(x[0]))
        merged = [(to_mins(sorted_ivs[0][0]), to_mins(sorted_ivs[0][1]))]

        for s, e in sorted_ivs[1:]:
            s_m, e_m = to_mins(s), to_mins(e)
            if s_m <= merged[-1][1]:
                merged[-1] = (merged[-1][0], max(merged[-1][1], e_m))
            else:
                merged.append((s_m, e_m))

        return [(from_mins(s), from_mins(e)) for s, e in merged]

    # ── Helper: Find Conflict End ────────────────────────────────────────────

    def _find_conflict_end(
        self,
        slot_start: datetime,
        slot_end: datetime,
        d: date_type,
        merged_blocks: list
    ):
        """
        Checks if (slot_start, slot_end) overlaps any blocked interval on date d.

        Returns:
          - The end datetime of the conflicting block if there IS a conflict, so
            the caller can jump past it.
          - None if there is NO conflict.
        """
        for b_start_t, b_end_t in merged_blocks:
            b_start_dt = datetime.combine(d, b_start_t)
            b_end_dt = datetime.combine(d, b_end_t)
            # Overlap if NOT (slot ends before block starts OR slot starts after block ends)
            if not (slot_end <= b_start_dt or slot_start >= b_end_dt):
                return b_end_dt  # Jump past this block
        return None

    # ── Helper: Parse Time String ────────────────────────────────────────────

    def _parse_time(self, t_str: str) -> time | None:
        """Parses routine time strings such as '8.00 AM', '08:00 AM', or '14:00'."""
        t_str = t_str.replace(".", ":").upper().strip()
        for fmt in ("%I:%M %p", "%I %p", "%H:%M"):
            try:
                dt = datetime.strptime(t_str, fmt)
                return dt.time()
            except ValueError:
                pass
        return None
