CREATE TABLE IF NOT EXISTS attendance_features (
    person_id TEXT NOT NULL,
    person_type TEXT NOT NULL CHECK (person_type IN ('student', 'staff')),
    date DATE NOT NULL,
    department TEXT, campus TEXT, course_id TEXT, faculty_id TEXT,
    scheduled_sessions INTEGER NOT NULL CHECK (scheduled_sessions > 0),
    attended_sessions INTEGER NOT NULL CHECK (attended_sessions BETWEEN 0 AND scheduled_sessions),
    late_sessions INTEGER NOT NULL CHECK (late_sessions BETWEEN 0 AND attended_sessions),
    engagement_score NUMERIC(5,2) CHECK (engagement_score BETWEEN 0 AND 100),
    assignment_submissions INTEGER,
    daily_attendance_rate NUMERIC(6,5), daily_late_rate NUMERIC(6,5),
    attendance_rate_7d NUMERIC(6,5), late_rate_7d NUMERIC(6,5),
    engagement_7d NUMERIC(6,2), at_risk SMALLINT CHECK (at_risk IN (0,1)),
    day_of_week SMALLINT, PRIMARY KEY (person_id,date)
);
CREATE INDEX IF NOT EXISTS idx_attendance_features_date ON attendance_features(date);
CREATE INDEX IF NOT EXISTS idx_attendance_features_department ON attendance_features(department,person_type);