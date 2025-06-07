-- AgenticPersona Integration Tables for Music Service Proxy
-- This migration adds tables for board consultations and user preferences

-- Table for storing board consultation results
CREATE TABLE IF NOT EXISTS board_consultations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    consultation_topic TEXT NOT NULL,
    consultation_context JSONB NOT NULL DEFAULT '{}',
    board_decision TEXT NOT NULL,
    decision_reasoning TEXT,
    confidence_score DECIMAL(3,2) CHECK (confidence_score >= 0 AND confidence_score <= 1),
    board_members_consulted JSONB NOT NULL DEFAULT '[]',
    consultation_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'
);

-- Table for storing user preferences related to AgenticPersona
CREATE TABLE IF NOT EXISTS agentic_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    preference_key VARCHAR(255) NOT NULL,
    preference_value JSONB NOT NULL,
    confidence_level DECIMAL(3,2) DEFAULT 0.5 CHECK (confidence_level >= 0 AND confidence_level <= 1),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, preference_key)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_consultations_user ON board_consultations(user_id);
CREATE INDEX IF NOT EXISTS idx_consultations_timestamp ON board_consultations(consultation_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_preferences_user ON agentic_preferences(user_id);

-- Comments for documentation
COMMENT ON TABLE board_consultations IS 'Stores AI board consultation results for music-related decisions';
COMMENT ON TABLE agentic_preferences IS 'Stores user preferences learned from AgenticPersona interactions';
COMMENT ON COLUMN board_consultations.confidence_score IS 'Confidence level of the board decision (0-1)';
COMMENT ON COLUMN agentic_preferences.confidence_level IS 'Confidence in the preference value (0-1)';