
-- -----------------------------------------------------
-- Table `horses_stats`
-- -----------------------------------------------------
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS `horses_stats`;
SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE `horses_stats` (
    `id`                            INT NOT NULL AUTO_INCREMENT,
    `horse_id`                     INT DEFAULT NULL,
    `race_id`                       VARCHAR(20) DEFAULT NULL,
    `races_lengths_id`              INT DEFAULT NULL,
    `entry_rating`                  INT DEFAULT NULL,
    `entry_fee`                     FLOAT DEFAULT NULL,
    `horse_class`                   INT DEFAULT NULL,
    `date_entry`                    DATETIME DEFAULT NULL,
    `position`                      INT DEFAULT NULL,
    `is_fire`                       TINYINT(1) DEFAULT NULL,
    `time_finish`                   FLOAT DEFAULT NULL,
    `date_updated`                  DATETIME DEFAULT NULL,
    `date_created`                  DATETIME DEFAULT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `race_id` (`race_id`) USING BTREE,
    INDEX `fk_horses_stats_races_lengths_idx` (`races_lengths_id` ASC),
    CONSTRAINT `fk_horses_stats_races_lengths` FOREIGN KEY (`races_lengths_id`) REFERENCES `races_lengths` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB;

DROP TRIGGER IF EXISTS `horses_stats_BEFORE_INSERT`;
CREATE TRIGGER `horses_stats_create` BEFORE INSERT ON `horses_stats` FOR EACH ROW SET NEW.date_created = NOW();

DROP TRIGGER IF EXISTS `horses_stats_BEFORE_UPDATE`;
CREATE TRIGGER `horses_stats_update` BEFORE UPDATE ON `horses_stats` FOR EACH ROW SET NEW.date_updated = NOW();
