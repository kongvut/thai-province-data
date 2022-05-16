/*

 Source Server         : bot4k
 Source Server Type    : MariaDB
 Source Server Version : 100515
 Source Host           : 192.168.31.11:3308
 Source Schema         : thai_data

 Target Server Type    : MariaDB
 Target Server Version : 100515
 File Encoding         : 65001

 Date: 16/05/2022 13:58:58
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for thai_geographies
-- ----------------------------
DROP TABLE IF EXISTS `thai_geographies`;
CREATE TABLE `thai_geographies` (
  `id` int(11) NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of thai_geographies
-- ----------------------------
BEGIN;
INSERT INTO `thai_geographies` (`id`, `name`) VALUES (1, 'ภาคเหนือ');
INSERT INTO `thai_geographies` (`id`, `name`) VALUES (2, 'ภาคกลาง');
INSERT INTO `thai_geographies` (`id`, `name`) VALUES (3, 'ภาคตะวันออกเฉียงเหนือ');
INSERT INTO `thai_geographies` (`id`, `name`) VALUES (4, 'ภาคตะวันตก');
INSERT INTO `thai_geographies` (`id`, `name`) VALUES (5, 'ภาคตะวันออก');
INSERT INTO `thai_geographies` (`id`, `name`) VALUES (6, 'ภาคใต้');
COMMIT;

SET FOREIGN_KEY_CHECKS = 1;
