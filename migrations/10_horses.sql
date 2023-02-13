
-- -----------------------------------------------------
-- Table `horses`
-- -----------------------------------------------------
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS `horses`;
SET FOREIGN_KEY_CHECKS = 1;


CREATE TABLE `horses` (
    `id`                            INT NOT NULL AUTO_INCREMENT,
    `horse_id`                      INT DEFAULT NULL,
    `bloodlines_id`                 INT DEFAULT NULL,
    `breeds_types_id`               INT DEFAULT NULL,
    `breeding_counter`              INT DEFAULT NULL,
    `breeding_decay_level`          INT DEFAULT NULL,
    `breeding_decay_limit`          INT DEFAULT NULL,
    `career_first`                  INT DEFAULT NULL,
    `career_second`                 INT DEFAULT NULL,
    `career_third`                  INT DEFAULT NULL,
    `offspring_count`               INT DEFAULT NULL,
    `parents_win_rate`              FLOAT DEFAULT NULL,
    `offspring_win_rate`            FLOAT DEFAULT NULL,
    `breeding_cycle_reset`          DATETIME DEFAULT NULL,
    `surface_preference`            INT DEFAULT NULL,
    `class`                         INT DEFAULT NULL,
    `type`                          VARCHAR(100) DEFAULT NULL,
    `genotypes_id`                  INT DEFAULT NULL,
    `hash_info_color`               VARCHAR(100) DEFAULT NULL,
    `hash_info_hex_code`            VARCHAR(100) DEFAULT NULL,
    `hash_info_name`                VARCHAR(255) DEFAULT NULL,
    `is_upgraded`                   TINYINT(1) DEFAULT NULL,
    `genders_id`                    INT DEFAULT NULL,
    `img_url`                       VARCHAR(255) DEFAULT NULL,
    `name`                          VARCHAR(255) DEFAULT NULL,
    `is_approved_for_racing`        TINYINT(1) DEFAULT NULL,
    `is_in_stud`                    TINYINT(1) DEFAULT NULL,
    `is_on_racing_contract`         TINYINT(1) DEFAULT NULL,
    `is_trial_horse`                TINYINT(1) DEFAULT NULL,
    `is_running_free_race`          TINYINT(1) DEFAULT NULL,
    `last_stud_duration`            INT DEFAULT NULL,
    `last_stud_timestamp`           INT DEFAULT NULL,
    `mating_price`                  BIGINT DEFAULT NULL,
    `next_breeding_date`            DATETIME DEFAULT NULL,
    `number_of_races`               INT DEFAULT NULL,
    `owners_id`                     INT DEFAULT NULL,
    `fathers_id`                    INT DEFAULT NULL,
    `mothers_id`                    INT DEFAULT NULL,
    `rating`                        INT DEFAULT NULL,
    `super_coat`                    TINYINT(1) DEFAULT NULL,
    `skin`                          VARCHAR(255) DEFAULT NULL,
    `coats_id`                      INT DEFAULT NULL,
    `tx`                            VARCHAR(255) DEFAULT NULL,
    `tx_date`                       DATETIME DEFAULT NULL,
    `win_rate`                      FLOAT DEFAULT NULL,
    `paid_win_rate`                 FLOAT DEFAULT NULL,
    `current_fatigue`               INT DEFAULT NULL,
    `current_stamina`               INT DEFAULT NULL,
    `time_to_full_recovery`         DATETIME DEFAULT NULL,
    `date_updated`                  DATETIME DEFAULT NULL,
    `date_created`                  DATETIME DEFAULT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `horse_id` (`horse_id`) USING BTREE,
    INDEX `fk_horses_bloodlines_idx` (`bloodlines_id` ASC),
    CONSTRAINT `fk_horses_bloodlines` FOREIGN KEY (`bloodlines_id`) REFERENCES `bloodlines` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION,
    INDEX `fk_horses_breeds_types_idx` (`breeds_types_id` ASC),
    CONSTRAINT `fk_horses_breeds_types` FOREIGN KEY (`breeds_types_id`) REFERENCES `breeds_types` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION,
    INDEX `fk_horses_genotypes_idx` (`genotypes_id` ASC),
    CONSTRAINT `fk_horses_genotypes` FOREIGN KEY (`genotypes_id`) REFERENCES `genotypes` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION,
    INDEX `fk_horses_genders_idx` (`genders_id` ASC),
    CONSTRAINT `fk_horses_genders` FOREIGN KEY (`genders_id`) REFERENCES `genders` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION,
    INDEX `fk_horses_coats_idx` (`coats_id` ASC),
    CONSTRAINT `fk_horses_coats` FOREIGN KEY (`coats_id`) REFERENCES `coats` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION,
    INDEX `fk_horses_owners_idx` (`owners_id` ASC),
    CONSTRAINT `fk_horses_owners` FOREIGN KEY (`owners_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION,
    INDEX `fk_horses_fathers_idx` (`fathers_id` ASC),
    CONSTRAINT `fk_horses_fathers` FOREIGN KEY (`fathers_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION,
    INDEX `fk_horses_mothers_idx` (`mothers_id` ASC),
    CONSTRAINT `fk_horses_mothers` FOREIGN KEY (`mothers_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB;

DROP TRIGGER IF EXISTS `horses_BEFORE_INSERT`;
CREATE TRIGGER `horses_create` BEFORE INSERT ON `horses` FOR EACH ROW SET NEW.date_created = NOW();

DROP TRIGGER IF EXISTS `horses_BEFORE_UPDATE`;
CREATE TRIGGER `horses_update` BEFORE UPDATE ON `horses` FOR EACH ROW SET NEW.date_updated = NOW();
