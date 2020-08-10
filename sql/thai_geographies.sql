/*
 Source Server Type    : MariaDB
 Source Server Version : 100412

 Target Server Type    : MariaDB
 Target Server Version : 100412
 File Encoding         : 65001

 Date: 10/08/2020 21:38:08
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for thai_geographies
-- ----------------------------
DROP TABLE IF EXISTS `thai_geographies`;
CREATE TABLE `thai_geographies` (
  `id` int(2) NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of thai_geographies
-- ----------------------------
BEGIN;
INSERT INTO `thai_geographies` VALUES (1, 'ภาคเหนือ');
INSERT INTO `thai_geographies` VALUES (2, 'ภาคกลาง');
INSERT INTO `thai_geographies` VALUES (3, 'ภาคตะวันออกเฉียงเหนือ');
INSERT INTO `thai_geographies` VALUES (4, 'ภาคตะวันตก');
INSERT INTO `thai_geographies` VALUES (5, 'ภาคตะวันออก');
INSERT INTO `thai_geographies` VALUES (6, 'ภาคใต้');
COMMIT;

SET FOREIGN_KEY_CHECKS = 1;
