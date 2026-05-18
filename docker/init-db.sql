-- Initialize PostgreSQL database for multi-tenant ERP system
-- This script runs once when the database is first created

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create a public schema table to track workspaces
CREATE TABLE IF NOT EXISTS public.workspaces (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Create index on slug for faster lookups
CREATE INDEX IF NOT EXISTS idx_workspaces_slug ON public.workspaces(slug);

-- Note: Individual workspace schemas will be created dynamically by the application
-- when a new workspace is registered. Each workspace will have its own schema
-- with isolated tables for inventory, pricing, financial data, etc.
