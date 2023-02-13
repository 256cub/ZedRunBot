
-- -----------------------------------------------------
-- Table `cities`
-- -----------------------------------------------------
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS `cities`;
SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE `cities` (
    `id`                            INT NOT NULL AUTO_INCREMENT,
    `name`                          VARCHAR(100) DEFAULT NULL,
    `countries_id`                  INT DEFAULT NULL,
    `date_updated`                  DATETIME DEFAULT NULL,
    `date_created`                  DATETIME DEFAULT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB;

DROP TRIGGER IF EXISTS `cities_BEFORE_INSERT`;
CREATE TRIGGER `cities_create` BEFORE INSERT ON `cities` FOR EACH ROW SET NEW.date_created = NOW();

DROP TRIGGER IF EXISTS `cities_BEFORE_UPDATE`;
CREATE TRIGGER `cities_update` BEFORE UPDATE ON `cities` FOR EACH ROW SET NEW.date_updated = NOW();
