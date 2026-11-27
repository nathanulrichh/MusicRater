-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema musicrater
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema musicrater
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `musicrater` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci ;
USE `musicrater` ;

-- -----------------------------------------------------
-- Table `musicrater`.`artists`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `musicrater`.`artists` (
  `artist_id` INT NOT NULL,
  `artist_name` VARCHAR(50) NULL DEFAULT NULL,
  PRIMARY KEY (`artist_id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `musicrater`.`albums`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `musicrater`.`albums` (
  `album_id` INT NOT NULL,
  `artist_id` INT NULL DEFAULT NULL,
  `album_name` VARCHAR(50) NOT NULL,
  `release_date` DATE NULL DEFAULT NULL,
  `cover_image_url` VARCHAR(50) NULL DEFAULT NULL,
  PRIMARY KEY (`album_id`),
  INDEX `artist_id` (`artist_id` ASC) VISIBLE,
  CONSTRAINT `albums_ibfk_1`
    FOREIGN KEY (`artist_id`)
    REFERENCES `musicrater`.`artists` (`artist_id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `musicrater`.`album_artists`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `musicrater`.`album_artists` (
  `album_id` INT NULL DEFAULT NULL,
  `artist_id` INT NULL DEFAULT NULL,
  INDEX `album_id` (`album_id` ASC) VISIBLE,
  INDEX `artist_id` (`artist_id` ASC) VISIBLE,
  CONSTRAINT `album_artists_ibfk_1`
    FOREIGN KEY (`album_id`)
    REFERENCES `musicrater`.`albums` (`album_id`),
  CONSTRAINT `album_artists_ibfk_2`
    FOREIGN KEY (`artist_id`)
    REFERENCES `musicrater`.`artists` (`artist_id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `musicrater`.`users`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `musicrater`.`users` (
  `user_id` INT AUTO_INCREMENT NOT NULL,
  `username` VARCHAR(50) NOT NULL,
  `email` VARCHAR(50) NULL DEFAULT NULL,
  `date_joined` DATE NULL DEFAULT NULL,
  PRIMARY KEY (`user_id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `musicrater`.`album_ratings`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `musicrater`.`album_ratings` (
  `rating_id` INT NOT NULL,
  `user_id` INT NULL DEFAULT NULL,
  `album_id` INT NULL DEFAULT NULL,
  `rating` FLOAT NULL DEFAULT NULL,
  `created_at` DATETIME NULL DEFAULT NULL,
  `updated_at` DATETIME NULL DEFAULT NULL,
  PRIMARY KEY (`rating_id`),
  INDEX `user_id` (`user_id` ASC) VISIBLE,
  INDEX `album_id` (`album_id` ASC) VISIBLE,
  CONSTRAINT `album_ratings_ibfk_1`
    FOREIGN KEY (`user_id`)
    REFERENCES `musicrater`.`users` (`user_id`),
  CONSTRAINT `album_ratings_ibfk_2`
    FOREIGN KEY (`album_id`)
    REFERENCES `musicrater`.`albums` (`album_id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `musicrater`.`songs`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `musicrater`.`songs` (
  `song_id` INT NOT NULL,
  `album_id` INT NULL DEFAULT NULL,
  `song_name` VARCHAR(50) NOT NULL,
  `duration_seconds` INT NULL DEFAULT NULL,
  `track_number` INT NULL DEFAULT NULL,
  PRIMARY KEY (`song_id`),
  INDEX `album_id` (`album_id` ASC) VISIBLE,
  CONSTRAINT `songs_ibfk_1`
    FOREIGN KEY (`album_id`)
    REFERENCES `musicrater`.`albums` (`album_id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `musicrater`.`song_artists`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `musicrater`.`song_artists` (
  `song_id` INT NULL DEFAULT NULL,
  `artist_id` INT NULL DEFAULT NULL,
  INDEX `song_id` (`song_id` ASC) VISIBLE,
  INDEX `artist_id` (`artist_id` ASC) VISIBLE,
  CONSTRAINT `song_artists_ibfk_1`
    FOREIGN KEY (`song_id`)
    REFERENCES `musicrater`.`songs` (`song_id`),
  CONSTRAINT `song_artists_ibfk_2`
    FOREIGN KEY (`artist_id`)
    REFERENCES `musicrater`.`artists` (`artist_id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `musicrater`.`song_ratings`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `musicrater`.`song_ratings` (
  `rating_id` INT NOT NULL,
  `user_id` INT NULL DEFAULT NULL,
  `song_id` INT NULL DEFAULT NULL,
  `rating` FLOAT NULL DEFAULT NULL,
  `created_at` DATETIME NULL DEFAULT NULL,
  `updated_at` DATETIME NULL DEFAULT NULL,
  PRIMARY KEY (`rating_id`),
  INDEX `user_id` (`user_id` ASC) VISIBLE,
  INDEX `song_id` (`song_id` ASC) VISIBLE,
  CONSTRAINT `song_ratings_ibfk_1`
    FOREIGN KEY (`user_id`)
    REFERENCES `musicrater`.`users` (`user_id`),
  CONSTRAINT `song_ratings_ibfk_2`
    FOREIGN KEY (`song_id`)
    REFERENCES `musicrater`.`songs` (`song_id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

-- Least-privilege account for the web app (change the password!)
CREATE USER IF NOT EXISTS 'webapp'@'localhost' IDENTIFIED BY 'ChangeMe!123';
GRANT SELECT, INSERT, UPDATE, DELETE ON webdemo.users TO 'webapp'@'localhost';
FLUSH PRIVILEGES;