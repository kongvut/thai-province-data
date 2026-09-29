CREATE TABLE `geographies` (
  `id` int(11) NOT NULL,
  `name_th` varchar(255) NOT NULL,
  `name_en` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `geographies` (`id`, `name_th`, `name_en`) VALUES
  (1, 'ภาคเหนือ', 'Northern'),
  (2, 'ภาคกลาง', 'Central'),
  (3, 'ภาคตะวันออกเฉียงเหนือ', 'Northeastern'),
  (4, 'ภาคตะวันตก', 'Western'),
  (5, 'ภาคตะวันออก', 'Eastern'),
  (6, 'ภาคใต้', 'Southern');
