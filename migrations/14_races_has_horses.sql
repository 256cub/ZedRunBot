
-- -----------------------------------------------------
-- Table `races_has_horses`
-- -----------------------------------------------------
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS `races_has_horses`;
SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE `races_has_horses` (
    `id`                            INT NOT NULL AUTO_INCREMENT,
    `races_id`                      INT DEFAULT NULL,
    `horses_id`                     INT DEFAULT NULL,
    `gate`                          INT DEFAULT NULL,
    `final_position`                INT DEFAULT NULL,
    `finish_time`                   FLOAT DEFAULT NULL,
    `date_updated`                  DATETIME DEFAULT NULL,
    `date_created`                  DATETIME DEFAULT NULL,
    PRIMARY KEY (`id`),
    INDEX `fk_races_has_horses_races_idx` (`races_id` ASC),
    CONSTRAINT `fk_races_has_horses_races` FOREIGN KEY (`races_id`) REFERENCES `races` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION,
    INDEX `fk_races_has_horses_horses_idx` (`horses_id` ASC),
    CONSTRAINT `fk_races_has_horses_horses` FOREIGN KEY (`horses_id`) REFERENCES `horses` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB;

DROP TRIGGER IF EXISTS `races_has_horses_BEFORE_INSERT`;
CREATE TRIGGER `races_has_horses_create` BEFORE INSERT ON `races_has_horses` FOR EACH ROW SET NEW.date_created = NOW();

DROP TRIGGER IF EXISTS `races_has_horses_BEFORE_UPDATE`;
CREATE TRIGGER `races_has_horses_update` BEFORE UPDATE ON `races_has_horses` FOR EACH ROW SET NEW.date_updated = NOW();
