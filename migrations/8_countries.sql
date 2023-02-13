
-- -----------------------------------------------------
-- Table `countries`
-- -----------------------------------------------------
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS `countries`;
SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE `countries` (
    `id`                            INT NOT NULL AUTO_INCREMENT,
    `name`                          VARCHAR(100) DEFAULT NULL,
    `code`                          VARCHAR(100) DEFAULT NULL,
    `date_updated`                  DATETIME DEFAULT NULL,
    `date_created`                  DATETIME DEFAULT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `name` (`name`) USING BTREE,
    UNIQUE KEY `code` (`code`) USING BTREE
) ENGINE=InnoDB;

DROP TRIGGER IF EXISTS `countries_BEFORE_INSERT`;
CREATE TRIGGER `countries_create` BEFORE INSERT ON `countries` FOR EACH ROW SET NEW.date_created = NOW();

DROP TRIGGER IF EXISTS `countries_BEFORE_UPDATE`;
CREATE TRIGGER `countries_update` BEFORE UPDATE ON `countries` FOR EACH ROW SET NEW.date_updated = NOW();
