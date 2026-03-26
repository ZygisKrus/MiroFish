"""
Academic Calendar Engine for VU Physics Faculty Simulation

Maps simulation days to academic context periods and provides
behavior multipliers that modify agent activity patterns based on
the academic calendar (normal semester, pre-exam, exam week, etc.)

Used by the simulation runner to apply realistic academic pressure
dynamics to agent behavior over a 28-day simulation window.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple


class AcademicPeriod(Enum):
    """Academic period types at VU Physics Faculty"""
    ORIENTATION_WEEK = "orientation_week"
    NORMAL_SEMESTER = "normal_semester"
    PRE_EXAM_WEEK = "pre_exam_week"
    EXAM_WEEK = "exam_week"        # "Sesija"
    POST_EXAM = "post_exam"
    FIDI = "fidi"                  # Fiziko Diena - Physics Day celebration


@dataclass
class BehaviorModifiers:
    """
    Multipliers applied to agent behavior during a specific academic period.

    All values are multipliers (1.0 = baseline).
    Values > 1.0 increase the behavior, < 1.0 decrease it.
    """
    # Study tool interest (how likely to seek/try Fizkonspektas)
    study_tool_interest: float = 1.0

    # Social media activity (Instagram, Telegram, Facebook)
    social_media_activity: float = 1.0

    # Word-of-mouth activity (physical conversations, dorm talk)
    word_of_mouth_activity: float = 1.0

    # Price sensitivity (higher = more resistant to paying)
    price_sensitivity: float = 1.0

    # Exam stress level (affects decision-making urgency)
    exam_stress: float = 1.0

    # Churn risk (likelihood of cancelling subscription)
    churn_risk: float = 1.0

    # Account sharing pressure (desire to split costs)
    account_sharing_pressure: float = 1.0

    # AI assistant usage interest
    ai_assistant_interest: float = 1.0

    # Overall activity level multiplier (affects all actions)
    overall_activity: float = 1.0

    # Free trial conversion pressure (urgency to decide before trial ends)
    trial_conversion_pressure: float = 1.0


# Pre-defined behavior modifiers for each academic period
PERIOD_MODIFIERS: Dict[AcademicPeriod, BehaviorModifiers] = {
    AcademicPeriod.ORIENTATION_WEEK: BehaviorModifiers(
        study_tool_interest=0.8,       # Not yet stressed about courses
        social_media_activity=1.5,     # Very active socially, exploring campus
        word_of_mouth_activity=1.8,    # Meeting new people constantly
        price_sensitivity=1.3,         # Careful with budget at start
        exam_stress=0.2,               # No exam pressure yet
        churn_risk=0.3,                # Just started, unlikely to churn
        account_sharing_pressure=0.5,  # Don't know enough people yet
        ai_assistant_interest=0.6,     # Don't know what they need yet
        overall_activity=1.3,          # High energy, exploring everything
        trial_conversion_pressure=0.3  # No urgency
    ),

    AcademicPeriod.NORMAL_SEMESTER: BehaviorModifiers(
        study_tool_interest=1.0,       # Baseline
        social_media_activity=1.0,     # Baseline
        word_of_mouth_activity=1.0,    # Baseline
        price_sensitivity=1.0,         # Baseline
        exam_stress=0.5,               # Low background stress
        churn_risk=0.8,                # Moderate - may cancel if not using
        account_sharing_pressure=1.0,  # Normal
        ai_assistant_interest=1.0,     # Normal
        overall_activity=1.0,          # Baseline
        trial_conversion_pressure=0.5  # Low urgency
    ),

    AcademicPeriod.PRE_EXAM_WEEK: BehaviorModifiers(
        study_tool_interest=2.5,       # Desperately seeking study aids
        social_media_activity=0.7,     # Less scrolling, more studying
        word_of_mouth_activity=1.5,    # "Hey did you hear about this app?"
        price_sensitivity=0.6,         # Less price-sensitive when desperate
        exam_stress=1.8,               # High stress
        churn_risk=0.1,                # Won't cancel before exams
        account_sharing_pressure=1.5,  # Trying to organize group buys quickly
        ai_assistant_interest=2.0,     # "I need a tutor RIGHT NOW"
        overall_activity=1.3,          # More active overall
        trial_conversion_pressure=1.5  # Starting to feel urgency
    ),

    AcademicPeriod.EXAM_WEEK: BehaviorModifiers(
        study_tool_interest=3.0,       # MAXIMUM desperation
        social_media_activity=0.4,     # Almost no social media
        word_of_mouth_activity=1.2,    # Still talking but less
        price_sensitivity=0.3,         # "I'll pay anything to pass"
        exam_stress=3.0,               # Maximum stress
        churn_risk=0.05,               # Absolutely won't cancel during exams
        account_sharing_pressure=0.8,  # No time to organize, just buy it
        ai_assistant_interest=3.0,     # "Please help me understand this NOW"
        overall_activity=1.5,          # Very active (studying late nights)
        trial_conversion_pressure=3.0  # "My trial expires and exam is tomorrow"
    ),

    AcademicPeriod.POST_EXAM: BehaviorModifiers(
        study_tool_interest=0.3,       # Relief, don't want to think about studying
        social_media_activity=1.8,     # Back to scrolling and celebrating
        word_of_mouth_activity=1.5,    # Sharing exam stories
        price_sensitivity=1.5,         # "Why am I paying 9.99 for something I don't need?"
        exam_stress=0.1,               # Relief
        churn_risk=2.5,                # HIGHEST churn risk - "I survived, cancel now"
        account_sharing_pressure=0.5,  # Don't care anymore
        ai_assistant_interest=0.3,     # Don't need it now
        overall_activity=1.2,          # Active but not academically
        trial_conversion_pressure=0.2  # No urgency at all
    ),

    AcademicPeriod.FIDI: BehaviorModifiers(
        study_tool_interest=0.5,       # Party time, not studying
        social_media_activity=2.0,     # Posting party photos
        word_of_mouth_activity=2.5,    # HUGE social event, tons of conversations
        price_sensitivity=0.8,         # In a good mood, more willing to spend
        exam_stress=0.1,               # Party mode
        churn_risk=0.5,                # Feeling good about VU
        account_sharing_pressure=0.5,  # Not thinking about it
        ai_assistant_interest=0.3,     # Not studying
        overall_activity=1.8,          # Very active socially
        trial_conversion_pressure=0.3  # Low urgency
    ),
}


@dataclass
class SimulationDayConfig:
    """Configuration for a single simulation day"""
    day_number: int                    # Day 1-28
    academic_period: AcademicPeriod
    modifiers: BehaviorModifiers
    is_weekend: bool = False
    special_event: Optional[str] = None  # e.g., "Prof. Vicas midterm", "FiDi party"


@dataclass
class AcademicCalendarConfig:
    """
    Configuration for the academic calendar overlay.

    Defines the sequence of academic periods across the 28-day simulation,
    starting from a configurable point in the semester.
    """
    # Which week of the semester does the simulation start?
    # Options: "early" (weeks 1-4), "mid" (weeks 5-10), "pre_exam" (weeks 11-13), "exam" (weeks 14-16)
    semester_start_point: str = "mid"

    # Duration of simulation in days
    total_days: int = 28

    # Custom events (day_number -> event description)
    custom_events: Dict[int, str] = field(default_factory=dict)

    # Whether FiDi falls within the simulation window
    include_fidi: bool = False
    fidi_day: Optional[int] = None  # Which day of simulation is FiDi


class AcademicCalendar:
    """
    Maps simulation days to academic context with behavior modifiers.

    Usage:
        calendar = AcademicCalendar(AcademicCalendarConfig(semester_start_point="pre_exam"))
        for day in range(1, 29):
            day_config = calendar.get_day_config(day)
            print(f"Day {day}: {day_config.academic_period.value}, stress={day_config.modifiers.exam_stress}")
    """

    # Pre-defined semester templates: maps day ranges to academic periods
    SEMESTER_TEMPLATES: Dict[str, List[Tuple[range, AcademicPeriod]]] = {
        "early": [
            # Orientation -> Normal semester (calm start)
            (range(1, 4), AcademicPeriod.ORIENTATION_WEEK),
            (range(4, 29), AcademicPeriod.NORMAL_SEMESTER),
        ],
        "mid": [
            # Normal semester -> building toward midterms
            (range(1, 15), AcademicPeriod.NORMAL_SEMESTER),
            (range(15, 22), AcademicPeriod.PRE_EXAM_WEEK),
            (range(22, 27), AcademicPeriod.EXAM_WEEK),
            (range(27, 29), AcademicPeriod.POST_EXAM),
        ],
        "pre_exam": [
            # High-pressure scenario: approaching exams fast
            (range(1, 8), AcademicPeriod.NORMAL_SEMESTER),
            (range(8, 15), AcademicPeriod.PRE_EXAM_WEEK),
            (range(15, 24), AcademicPeriod.EXAM_WEEK),
            (range(24, 29), AcademicPeriod.POST_EXAM),
        ],
        "exam": [
            # Maximum pressure: exam week starts immediately
            (range(1, 4), AcademicPeriod.PRE_EXAM_WEEK),
            (range(4, 18), AcademicPeriod.EXAM_WEEK),
            (range(18, 29), AcademicPeriod.POST_EXAM),
        ],
    }

    def __init__(self, config: Optional[AcademicCalendarConfig] = None):
        self.config = config or AcademicCalendarConfig()
        self._day_configs: Dict[int, SimulationDayConfig] = {}
        self._build_calendar()

    def _build_calendar(self):
        """Build the day-by-day calendar from the template"""
        template_key = self.config.semester_start_point
        if template_key not in self.SEMESTER_TEMPLATES:
            template_key = "mid"  # Default fallback

        template = self.SEMESTER_TEMPLATES[template_key]

        for day in range(1, self.config.total_days + 1):
            # Find academic period for this day
            period = AcademicPeriod.NORMAL_SEMESTER  # default
            for day_range, period_type in template:
                if day in day_range:
                    period = period_type
                    break

            # Check for FiDi override
            if self.config.include_fidi and self.config.fidi_day == day:
                period = AcademicPeriod.FIDI

            # Determine if weekend (assuming day 1 = Monday)
            is_weekend = (day % 7) in (6, 0)  # Saturday = 6, Sunday = 0

            # Get modifiers for this period
            base_modifiers = PERIOD_MODIFIERS.get(period, BehaviorModifiers())

            # Weekend adjustments
            if is_weekend:
                modifiers = BehaviorModifiers(
                    study_tool_interest=base_modifiers.study_tool_interest * 0.6,
                    social_media_activity=base_modifiers.social_media_activity * 1.3,
                    word_of_mouth_activity=base_modifiers.word_of_mouth_activity * 0.7,
                    price_sensitivity=base_modifiers.price_sensitivity,
                    exam_stress=base_modifiers.exam_stress * 0.7,
                    churn_risk=base_modifiers.churn_risk * 1.2,
                    account_sharing_pressure=base_modifiers.account_sharing_pressure,
                    ai_assistant_interest=base_modifiers.ai_assistant_interest * 0.5,
                    overall_activity=base_modifiers.overall_activity * 0.8,
                    trial_conversion_pressure=base_modifiers.trial_conversion_pressure * 0.8,
                )
            else:
                modifiers = base_modifiers

            # Custom events
            special_event = self.config.custom_events.get(day)

            self._day_configs[day] = SimulationDayConfig(
                day_number=day,
                academic_period=period,
                modifiers=modifiers,
                is_weekend=is_weekend,
                special_event=special_event,
            )

    def get_day_config(self, day: int) -> SimulationDayConfig:
        """Get the configuration for a specific simulation day"""
        if day not in self._day_configs:
            return SimulationDayConfig(
                day_number=day,
                academic_period=AcademicPeriod.NORMAL_SEMESTER,
                modifiers=PERIOD_MODIFIERS[AcademicPeriod.NORMAL_SEMESTER],
            )
        return self._day_configs[day]

    def get_round_config(self, round_number: int, rounds_per_day: int = 4) -> SimulationDayConfig:
        """
        Get config for a specific simulation round.

        Args:
            round_number: 1-indexed round number (1 to total_days * rounds_per_day)
            rounds_per_day: Number of rounds per day (default 4)

        Returns:
            SimulationDayConfig for the day containing this round
        """
        day = ((round_number - 1) // rounds_per_day) + 1
        return self.get_day_config(day)

    def get_all_configs(self) -> List[SimulationDayConfig]:
        """Get all day configurations in order"""
        return [self._day_configs[d] for d in sorted(self._day_configs.keys())]

    def get_period_summary(self) -> Dict[str, int]:
        """Get a summary of how many days are in each period"""
        summary: Dict[str, int] = {}
        for config in self._day_configs.values():
            period_name = config.academic_period.value
            summary[period_name] = summary.get(period_name, 0) + 1
        return summary

    def get_peak_conversion_days(self) -> List[int]:
        """
        Identify days with highest expected conversion potential.

        Returns days where study_tool_interest * (1/price_sensitivity) is highest.
        """
        scored_days = []
        for day, config in self._day_configs.items():
            score = config.modifiers.study_tool_interest / max(0.1, config.modifiers.price_sensitivity)
            scored_days.append((day, score))

        scored_days.sort(key=lambda x: x[1], reverse=True)
        top_n = max(1, len(scored_days) // 4)
        return [day for day, _ in scored_days[:top_n]]


# Convenience factory functions

def create_midterm_calendar(fidi_day: Optional[int] = None) -> AcademicCalendar:
    """Create calendar starting mid-semester, building to midterms"""
    config = AcademicCalendarConfig(
        semester_start_point="mid",
        include_fidi=fidi_day is not None,
        fidi_day=fidi_day,
    )
    return AcademicCalendar(config)


def create_exam_panic_calendar() -> AcademicCalendar:
    """Create calendar with immediate exam pressure (worst case scenario)"""
    config = AcademicCalendarConfig(
        semester_start_point="exam",
        custom_events={
            3: "Prof. Vicas Calculus I midterm announced",
            5: "Quantum Mechanics exam date posted",
            10: "Calculus I midterm",
            14: "QM exam",
            16: "Electrodynamics exam",
        },
    )
    return AcademicCalendar(config)


def create_fresh_start_calendar() -> AcademicCalendar:
    """Create calendar starting at orientation (best for testing awareness spread)"""
    config = AcademicCalendarConfig(
        semester_start_point="early",
        custom_events={
            1: "VU Physics Faculty orientation day",
            2: "Kamciatka dorm move-in day",
            7: "First week of lectures begins",
        },
    )
    return AcademicCalendar(config)
