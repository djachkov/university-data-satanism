CREATE TABLE schools (
    school_id INT AUTO_INCREMENT PRIMARY KEY,
    school_name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE spells (
    spell_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    level INT NOT NULL,
    school_id INT NOT NULL,
    cast_time VARCHAR(50),
    spell_range VARCHAR(100),
    duration VARCHAR(100),
    description TEXT,
    FOREIGN KEY (school_id) REFERENCES schools(school_id) ON DELETE CASCADE
);

CREATE TABLE classes (
    class_id INT AUTO_INCREMENT PRIMARY KEY,
    class_name VARCHAR(100) UNIQUE NOT NULL
);


CREATE TABLE spell_components (
    component_id INT AUTO_INCREMENT PRIMARY KEY,
    spell_id INT NOT NULL,
    verbal BOOLEAN NOT NULL,
    somatic BOOLEAN NOT NULL,
    material BOOLEAN NOT NULL,
    material_cost TEXT,
    FOREIGN KEY (spell_id) REFERENCES spells(spell_id) ON DELETE CASCADE
);


CREATE TABLE spells_classes (
    spell_id INT NOT NULL,
    class_id INT NOT NULL,
    PRIMARY KEY (spell_id, class_id),
    FOREIGN KEY (spell_id) REFERENCES spells(spell_id) ON DELETE CASCADE,
    FOREIGN KEY (class_id) REFERENCES classes(class_id) ON DELETE CASCADE
);
