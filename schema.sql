-- 1. Tabela POTRZEBUJĄCY
CREATE TABLE IF NOT EXISTS potrzebujacy (
    id_potrzebujacego SERIAL PRIMARY KEY,
    imie VARCHAR(100) NOT NULL,
    nazwisko VARCHAR(100) NOT NULL,
    numer_telefonu VARCHAR(20) NOT NULL unique,
    adres_potrzebujacego VARCHAR(255) not null,
	dlugosc_geograficzna DECIMAL(9, 6),
    szerokosc_geograficzna DECIMAL(8, 6)
);

-- 2. Tabela WOLONTARIUSZE
CREATE TABLE IF NOT EXISTS wolontariusze (
    id_wolontariusza SERIAL PRIMARY KEY,
    imie VARCHAR(100) NOT NULL,
    nazwisko VARCHAR(100) NOT NULL,
    pkt INT NOT NULL DEFAULT 0 CHECK (pkt >= 0),
    numer_telefonu VARCHAR(20) NOT NULL unique,
    adres_wolontariusza VARCHAR(255) not null,
    organizacja VARCHAR(255) not null,
    dlugosc_geograficzna DECIMAL(9, 6),
    szerokosc_geograficzna DECIMAL(8, 6)
);

-- 3. Tabela POTRZEBA (słownik, np. Zakupy, Leki)
CREATE TABLE IF NOT EXISTS potrzeba (
    id_potrzeba SERIAL PRIMARY KEY,
    id_potrzebujacego INT not null,
    opis VARCHAR(255),
    nazwa_potrzeba VARCHAR(150) NOT NULL
);

-- 4. Tabela HASLA (osobna tabela do logowania)
CREATE TABLE IF NOT EXISTS hasla_potrzebujacych (
    id SERIAL PRIMARY KEY,
    nr_tel VARCHAR(20) NOT NULL UNIQUE,
    haslo VARCHAR(255) NOT null,
    CONSTRAINT fk_haslo_potrzebujacy_tel
        FOREIGN KEY (nr_tel)
        REFERENCES potrzebujacy(numer_telefonu)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS hasla_wolontariuszy (
    id SERIAL PRIMARY KEY,
    nr_tel VARCHAR(20) NOT NULL UNIQUE,
    haslo VARCHAR(255) NOT null,
    CONSTRAINT fk_haslo_wolontariusz_tel
        FOREIGN KEY (nr_tel)
        REFERENCES wolontariusze(numer_telefonu)
        ON DELETE CASCADE
);

-- 5. Tabela PRZYPISANIE (łączy wszystko w całość)
CREATE TABLE IF NOT EXISTS przypisanie (
    id_przypisania SERIAL PRIMARY KEY,
    id_potrzeba INT NOT NULL,
    id_potrzebujacego INT NOT NULL, -- Dodane, aby wiedzieć komu pomagamy!
    id_wolontariusza INT,           -- Może być puste (NULL), dopóki ktoś nie przyjmie zgłoszenia
    status VARCHAR(50) DEFAULT 'oczekuje',

    CONSTRAINT fk_potrzeba FOREIGN KEY (id_potrzeba) REFERENCES potrzeba(id_potrzeba) ON DELETE CASCADE,
    CONSTRAINT fk_potrzebujacy FOREIGN KEY (id_potrzebujacego) REFERENCES potrzebujacy(id_potrzebujacego) ON DELETE CASCADE,
    CONSTRAINT fk_wolontariusz FOREIGN KEY (id_wolontariusza) REFERENCES wolontariusze(id_wolontariusza) ON DELETE SET NULL
);