CREATE TABLE "Student" (
    "StudentID" SERIAL PRIMARY KEY,
    "FullName" VARCHAR(255),
    "Email" VARCHAR(254),
    "ConsentStatus" VARCHAR(50),
    "ConsentVersion" VARCHAR(20),
    "ConsentTextHash" VARCHAR(64),
    "ConsentMethod" VARCHAR(100),
    "EnrollmentDate" DATE,
    "CourseList" TEXT[]
);

CREATE TABLE "Course" (
    "CourseID" SERIAL PRIMARY KEY,
    "CourseName" VARCHAR(255),
    "CourseCode" VARCHAR(20),
    "InstructorID" INTEGER
);

CREATE TABLE "Session" (
    "SessionID" SERIAL PRIMARY KEY,
    "CourseID" INTEGER REFERENCES "Course"("CourseID"),
    "InstructorID" INTEGER,
    "StartTime" TIMESTAMPTZ,
    "EndTime" TIMESTAMPTZ,
    "AttendanceWindowBefore" INTEGER,
    "AttendanceWindowAfter" INTEGER,
    "Status" VARCHAR(50)
);

CREATE TABLE "Camera" (
    "CameraID" SERIAL PRIMARY KEY,
    "Location" VARCHAR(255),
    "StreamURL" VARCHAR(255),
    "Resolution" VARCHAR(20),
    "FOV" NUMERIC,
    "TimeZone" VARCHAR(100),
    "Status" VARCHAR(50)
);

CREATE TABLE "SessionCamera" (
    "SessionID" INTEGER REFERENCES "Session"("SessionID"),
    "CameraID" INTEGER REFERENCES "Camera"("CameraID")
);

CREATE TABLE "AttendanceRecord" (
    "RecordID" SERIAL PRIMARY KEY,
    "SessionID" INTEGER REFERENCES "Session"("SessionID"),
    "StudentID" INTEGER REFERENCES "Student"("StudentID"),
    "PresentFlag" BOOLEAN,
    "FirstSeenAt" TIMESTAMPTZ,
    "LastSeenAt" TIMESTAMPTZ,
    "CumulativeSecondsVisible" INTEGER,
    "AverageConfidence" NUMERIC,
    "CamerasSeen" INTEGER[],
    "IsManualOverride" BOOLEAN
);

CREATE TABLE "Embedding" (
    "EmbeddingID" SERIAL PRIMARY KEY,
    "StudentID" INTEGER REFERENCES "Student"("StudentID"),
    "CreatedAt" TIMESTAMPTZ,
    "SourceImageRef" VARCHAR(512),
    "EmbeddingModelVersion" VARCHAR(50),
    "Vector" NUMERIC[]
);

CREATE TABLE "AuditLog" (
    "LogID" SERIAL PRIMARY KEY,
    "ActorID" VARCHAR(100),
    "Action" VARCHAR(50),
    "Target" VARCHAR(255),
    "Timestamp" TIMESTAMPTZ,
    "Details" TEXT,
    "PreviousValue" JSONB,
    "NewValue" JSONB
);

CREATE TABLE "LegalHold" (
    "HoldID" SERIAL PRIMARY KEY,
    "StudentID" INTEGER REFERENCES "Student"("StudentID"),
    "HoldReason" TEXT,
    "HoldStart" DATE,
    "HoldEnd" DATE,
    "HoldOpen" BOOLEAN
);

CREATE TABLE "Instructor" (
    "InstructorID" SERIAL PRIMARY KEY,
    "FullName" VARCHAR(255),
    "Email" VARCHAR(254),
    "Department" VARCHAR(100)
);

-- dafega