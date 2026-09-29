CREATE TABLE `geographies` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `geographies` (`id`, `name`) VALUES
  (1, 'ภาคเหนือ'),
  (2, 'ภาคกลาง'),
  (3, 'ภาคตะวันออกเฉียงเหนือ'),
  (4, 'ภาคตะวันตก'),
  (5, 'ภาคตะวันออก'),
  (6, 'ภาคใต้');
