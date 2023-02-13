
-- -----------------------------------------------------
-- Table `weathers`
-- -----------------------------------------------------
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS `weathers`;
SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE `weathers` (
    `id`                            INT NOT NULL AUTO_INCREMENT,
    `name`                          VARCHAR(100) DEFAULT NULL,
    `date_updated`                  DATETIME DEFAULT NULL,
    `date_created`                  DATETIME DEFAULT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `name` (`name`) USING BTREE
) ENGINE=InnoDB;

DROP TRIGGER IF EXISTS `weathers_BEFORE_INSERT`;
CREATE TRIGGER `weathers_create` BEFORE INSERT ON `weathers` FOR EACH ROW SET NEW.date_created = NOW();

DROP TRIGGER IF EXISTS `weathers_BEFORE_UPDATE`;
CREATE TRIGGER `weathers_update` BEFORE UPDATE ON `weathers` FOR EACH ROW SET NEW.date_updated = NOW();
