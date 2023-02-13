
-- -----------------------------------------------------
-- Table `coats`
-- -----------------------------------------------------
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS `coats`;
SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE `coats` (
    `id`                            INT NOT NULL AUTO_INCREMENT,
    `name`                          VARCHAR(100) DEFAULT NULL,
    `rate`                          INT DEFAULT NULL,
    `date_updated`                  DATETIME DEFAULT NULL,
    `date_created`                  DATETIME DEFAULT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `name` (`name`) USING BTREE
) ENGINE=InnoDB;

DROP TRIGGER IF EXISTS `coats_BEFORE_INSERT`;
CREATE TRIGGER `coats_create` BEFORE INSERT ON `coats` FOR EACH ROW SET NEW.date_created = NOW();

DROP TRIGGER IF EXISTS `coats_BEFORE_UPDATE`;
CREATE TRIGGER `coats_update` BEFORE UPDATE ON `coats` FOR EACH ROW SET NEW.date_updated = NOW();
