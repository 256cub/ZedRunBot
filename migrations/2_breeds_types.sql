
-- -----------------------------------------------------
-- Table `breeds_types`
-- -----------------------------------------------------
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS `breeds_types`;
SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE `breeds_types` (
    `id`                            INT NOT NULL AUTO_INCREMENT,
    `name`                          VARCHAR(100) DEFAULT NULL,
    `rate`                          INT DEFAULT NULL,
    `date_updated`                  DATETIME DEFAULT NULL,
    `date_created`                  DATETIME DEFAULT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `name` (`name`) USING BTREE
) ENGINE=InnoDB;

DROP TRIGGER IF EXISTS `breeds_types_BEFORE_INSERT`;
CREATE TRIGGER `breeds_types_create` BEFORE INSERT ON `breeds_types` FOR EACH ROW SET NEW.date_created = NOW();

DROP TRIGGER IF EXISTS `breeds_types_BEFORE_UPDATE`;
CREATE TRIGGER `breeds_types_update` BEFORE UPDATE ON `breeds_types` FOR EACH ROW SET NEW.date_updated = NOW();
