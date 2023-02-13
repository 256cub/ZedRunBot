
-- -----------------------------------------------------
-- Table `races_lengths`
-- -----------------------------------------------------
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS `races_lengths`;
SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE `races_lengths` (
    `id`                            INT NOT NULL AUTO_INCREMENT,
    `name`                          INT DEFAULT NULL,
    `date_updated`                  DATETIME DEFAULT NULL,
    `date_created`                  DATETIME DEFAULT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `name` (`name`) USING BTREE
) ENGINE=InnoDB;

DROP TRIGGER IF EXISTS `races_lengths_BEFORE_INSERT`;
CREATE TRIGGER `races_lengths_create` BEFORE INSERT ON `races_lengths` FOR EACH ROW SET NEW.date_created = NOW();

DROP TRIGGER IF EXISTS `races_lengths_BEFORE_UPDATE`;
CREATE TRIGGER `races_lengths_update` BEFORE UPDATE ON `races_lengths` FOR EACH ROW SET NEW.date_updated = NOW();
