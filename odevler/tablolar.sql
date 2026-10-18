CREATE TABLE Poliklinik (
    poliklinik_id INT PRIMARY KEY AUTO_INCREMENT,
    poliklinik_adi VARCHAR(100) NOT NULL
);

CREATE TABLE Doktor (
    doktor_id INT PRIMARY KEY AUTO_INCREMENT,
    ad VARCHAR(50) NOT NULL,
    soyad VARCHAR(50) NOT NULL,
    unvan VARCHAR(50),
    poliklinik_id INT,
    FOREIGN KEY (poliklinik_id) REFERENCES Poliklinik(poliklinik_id)
);

CREATE TABLE Servis (
    servis_id INT PRIMARY KEY AUTO_INCREMENT,
    servis_adi VARCHAR(100) NOT NULL,
    poliklinik_id INT,
    FOREIGN KEY (poliklinik_id) REFERENCES Poliklinik(poliklinik_id)
);

CREATE TABLE Hemsire (
    hemsire_id INT PRIMARY KEY AUTO_INCREMENT,
    ad VARCHAR(50) NOT NULL,
    soyad VARCHAR(50) NOT NULL,
    servis_id INT,
    FOREIGN KEY (servis_id) REFERENCES Servis(servis_id)
);

CREATE TABLE Hasta (
    hasta_id INT PRIMARY KEY AUTO_INCREMENT,
    tc_no CHAR(11) UNIQUE NOT NULL,
    ad VARCHAR(50) NOT NULL,
    soyad VARCHAR(50) NOT NULL,
    telefon VARCHAR(15)
);

CREATE TABLE Laboratuvar (
    lab_id INT PRIMARY KEY AUTO_INCREMENT,
    lab_adi VARCHAR(100) NOT NULL
);

CREATE TABLE Tahlil (
    tahlil_id INT PRIMARY KEY AUTO_INCREMENT,
    tahlil_adi VARCHAR(100) NOT NULL,
    lab_id INT,
    FOREIGN KEY (lab_id) REFERENCES Laboratuvar(lab_id)
);

CREATE TABLE Muayene (
    muayene_id INT PRIMARY KEY AUTO_INCREMENT,
    hasta_id INT,
    poliklinik_id INT,
    muayene_tarihi DATE,
    FOREIGN KEY (hasta_id) REFERENCES Hasta(hasta_id),
    FOREIGN KEY (poliklinik_id) REFERENCES Poliklinik(poliklinik_id)
);

CREATE TABLE Hasta_Tahlil (
    islem_id INT PRIMARY KEY AUTO_INCREMENT,
    hasta_id INT,
    tahlil_id INT,
    doktor_id INT,
    tahlil_tarihi DATE,
    sonuc VARCHAR(255),
    FOREIGN KEY (hasta_id) REFERENCES Hasta(hasta_id),
    FOREIGN KEY (tahlil_id) REFERENCES Tahlil(tahlil_id),
    FOREIGN KEY (doktor_id) REFERENCES Doktor(doktor_id)
);