
-- -----------------------------------------------------
-- Table `races_results`
-- -----------------------------------------------------
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS `races_results`;
SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE `races_results` (
    `id`                            INT NOT NULL AUTO_INCREMENT,
    `races_id`                      INT DEFAULT NULL,
    `horses_id`                     INT DEFAULT NULL,
    `class`                         INT DEFAULT NULL,
    `fee`                           FLOAT DEFAULT NULL,
    `races_lengths_id`              INT DEFAULT NULL,
    `name`                          VARCHAR(255) DEFAULT NULL,
    `prize_pool_first`              INT DEFAULT NULL,
    `prize_pool_second`             INT DEFAULT NULL,
    `prize_pool_third`              INT DEFAULT NULL,
    `prize_pool_total`              INT DEFAULT NULL,
    `race_id`                       INT DEFAULT NULL,
    `start_time`                    DATETIME DEFAULT NULL,
    `status`                        ENUM('finished', 'opened') DEFAULT NULL,
    `weathers_id`                   INT DEFAULT NULL,
    `rate`                          VARCHAR(20) DEFAULT NULL,
    `date_updated`                  DATETIME DEFAULT NULL,
    `date_created`                  DATETIME DEFAULT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `race_id` (`race_id`) USING BTREE,
    INDEX `fk_races_results_races_idx` (`races_id` ASC),
    CONSTRAINT `fk_races_results_races` FOREIGN KEY (`races_id`) REFERENCES `races` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION,
    INDEX `fk_races_results_horses_idx` (`horses_id` ASC),
    CONSTRAINT `fk_races_results_horses` FOREIGN KEY (`horses_id`) REFERENCES `horses` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION,
    INDEX `fk_races_results_races_lengths_idx` (`races_lengths_id` ASC),
    CONSTRAINT `fk_races_results_races_lengths` FOREIGN KEY (`races_lengths_id`) REFERENCES `races_lengths` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION,
    INDEX `fk_races_results_weathers_idx` (`weathers_id` ASC),
    CONSTRAINT `fk_races_results_weathers` FOREIGN KEY (`weathers_id`) REFERENCES `weathers` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB;

DROP TRIGGER IF EXISTS `races_results_BEFORE_INSERT`;
CREATE TRIGGER `races_results_create` BEFORE INSERT ON `races_results` FOR EACH ROW SET NEW.date_created = NOW();

DROP TRIGGER IF EXISTS `races_results_BEFORE_UPDATE`;
CREATE TRIGGER `races_results_update` BEFORE UPDATE ON `races_results` FOR EACH ROW SET NEW.date_updated = NOW();
