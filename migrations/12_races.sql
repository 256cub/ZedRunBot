
-- -----------------------------------------------------
-- Table `races`
-- -----------------------------------------------------
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS `races`;
SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE `races` (
    `id`                            INT NOT NULL AUTO_INCREMENT,
    `cities_id`                     INT DEFAULT NULL,
    `countries_id`                  INT DEFAULT NULL,
    `class`                         INT DEFAULT NULL,
    `fee`                           FLOAT DEFAULT NULL,
    `races_lengths_id`              INT DEFAULT NULL,
    `name`                          VARCHAR(255) DEFAULT NULL,
    `prize_pool_first`              BIGINT DEFAULT NULL,
    `prize_pool_second`             BIGINT DEFAULT NULL,
    `prize_pool_third`              BIGINT DEFAULT NULL,
    `prize_pool_total`              BIGINT DEFAULT NULL,
    `race_id`                       VARCHAR(20) DEFAULT NULL,
    `start_time`                    DATETIME DEFAULT NULL,
    `status`                        ENUM('finished', 'open') DEFAULT NULL,
    `weathers_id`                   INT DEFAULT NULL,
    `rate`                          INT DEFAULT NULL,
    `date_updated`                  DATETIME DEFAULT NULL,
    `date_created`                  DATETIME DEFAULT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `race_id` (`race_id`) USING BTREE,
    INDEX `fk_horses_cities_idx` (`cities_id` ASC),
    CONSTRAINT `fk_horses_cities` FOREIGN KEY (`cities_id`) REFERENCES `cities` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION,
    INDEX `fk_horses_countries_idx` (`countries_id` ASC),
    CONSTRAINT `fk_horses_countries` FOREIGN KEY (`countries_id`) REFERENCES `countries` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION,
    INDEX `fk_horses_races_lengths_idx` (`races_lengths_id` ASC),
    CONSTRAINT `fk_horses_races_lengths` FOREIGN KEY (`races_lengths_id`) REFERENCES `races_lengths` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION,
    INDEX `fk_horses_weathers_idx` (`weathers_id` ASC),
    CONSTRAINT `fk_horses_weathers` FOREIGN KEY (`weathers_id`) REFERENCES `weathers` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB;

DROP TRIGGER IF EXISTS `races_BEFORE_INSERT`;
CREATE TRIGGER `races_create` BEFORE INSERT ON `races` FOR EACH ROW SET NEW.date_created = NOW();

DROP TRIGGER IF EXISTS `races_BEFORE_UPDATE`;
CREATE TRIGGER `races_update` BEFORE UPDATE ON `races` FOR EACH ROW SET NEW.date_updated = NOW();
