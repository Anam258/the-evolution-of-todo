name: database-schema-design
description: Design relational database schemas, create tables, and manage migrations using best practices. Use for backend and data-driven applications.
---

# Database Schema Design

## Instructions

1. **Schema Planning**
   - Identify entities and relationships
   - Define primary and foreign keys
   - Normalize data (avoid duplication)

2. **Table Creation**
   - Use appropriate data types
   - Add constraints (NOT NULL, UNIQUE, CHECK)
   - Define indexes for performance

3. **Migrations**
   - Create versioned migration files
   - Support up and down migrations
   - Ensure backward compatibility

4. **Relationships**
   - One-to-One
   - One-to-Many
   - Many-to-Many (junction tables)

## Best Practices
- Use snake_case for table and column names
- Always define a primary key
- Avoid over-normalization
- Add timestamps (`created_at`, `updated_at`)
- Keep migrations small and reversible
- Never edit old migrations in production

## Example Structure

```sql
-- users table
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- posts table
CREATE TABLE posts (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
  title VARCHAR(255) NOT NULL,
  body TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);