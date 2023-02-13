
-- -----------------------------------------------------
-- Table `users`
-- -----------------------------------------------------
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS `users`;
SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE `users` (
    `id`                INT NOT NULL AUTO_INCREMENT,
    `address`           VARCHAR(255) DEFAULT NULL,
    `stable_name`       VARCHAR(255) DEFAULT NULL,
    `stable_slug`       VARCHAR(255) DEFAULT NULL,
    `profile_img_url`   VARCHAR(255) DEFAULT NULL,
    `date_updated`      DATETIME DEFAULT NULL,
    `date_created`      DATETIME DEFAULT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `address` (`address`) USING BTREE,
    UNIQUE KEY `stable_name` (`stable_name`) USING BTREE
) ENGINE=InnoDB;

DROP TRIGGER IF EXISTS `users_BEFORE_INSERT`;
CREATE TRIGGER `users_create` BEFORE INSERT ON `users` FOR EACH ROW SET NEW.date_created = NOW();

DROP TRIGGER IF EXISTS `users_BEFORE_UPDATE`;
CREATE TRIGGER `users_update` BEFORE UPDATE ON `users` FOR EACH ROW SET NEW.date_updated = NOW();
