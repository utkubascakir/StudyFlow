-- SEQUENCE
CREATE SEQUENCE seq_user_id START 10000 INCREMENT 1;

-- USERS TABLE
CREATE TABLE users (
    user_id INT PRIMARY KEY DEFAULT nextval('seq_user_id'),
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    user_password VARCHAR(255) NOT NULL,
    user_role VARCHAR(20) DEFAULT 'student' NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_user_role CHECK (user_role IN ('admin', 'student'))
);

-- STUDY ROOMS TABLE
CREATE TABLE study_rooms (
    room_id SERIAL PRIMARY KEY,
    room_name VARCHAR(50) NOT NULL,
    capacity INT NOT NULL,
    CONSTRAINT chk_capacity_positive CHECK (capacity > 0)
);

-- STUDY TABLES
CREATE TABLE study_tables (
    table_id SERIAL PRIMARY KEY,
    room_id INT REFERENCES study_rooms(room_id) ON DELETE CASCADE,
    table_number INT NOT NULL,
    is_available BOOLEAN DEFAULT TRUE,
    CONSTRAINT chk_table_num_pos CHECK (table_number > 0),
    CONSTRAINT uq_room_table_no UNIQUE (room_id, table_number)
);

-- RESERVATIONS TABLE
CREATE TABLE reservations (
    reservation_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    table_id INT REFERENCES study_tables(table_id) ON DELETE CASCADE,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    status VARCHAR(20) DEFAULT 'active' NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_res_status CHECK (status IN ('active', 'completed', 'cancelled')),
    CONSTRAINT chk_time_valid CHECK (end_time > start_time)
);