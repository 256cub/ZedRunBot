
-- -----------------------------------------------------
-- Table `bloodlines`
-- -----------------------------------------------------
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS `bloodlines`;
SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE `bloodlines` (
    `id`                            INT NOT NULL AUTO_INCREMENT,
    `name`                          VARCHAR(100) DEFAULT NULL,
    `rate`                          INT DEFAULT NULL,
    `date_updated`                  DATETIME DEFAULT NULL,
    `date_created`                  DATETIME DEFAULT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `name` (`name`) USING BTREE
) ENGINE=InnoDB;

DROP TRIGGER IF EXISTS `bloodlines_BEFORE_INSERT`;
CREATE TRIGGER `bloodlines_create` BEFORE INSERT ON `bloodlines` FOR EACH ROW SET NEW.date_created = NOW();

DROP TRIGGER IF EXISTS `bloodlines_BEFORE_UPDATE`;
CREATE TRIGGER `bloodlines_update` BEFORE UPDATE ON `bloodlines` FOR EACH ROW SET NEW.date_updated = NOW();
