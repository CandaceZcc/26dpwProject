
-- --------------------------------------------------------

--
-- 表的结构 `genres`
--

CREATE TABLE `genres` (
  `genres_id` bigint(20) NOT NULL,
  `genres_name` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- 转存表中的数据 `genres`
--

INSERT INTO `genres` (`genres_id`, `genres_name`) VALUES
(12, 'Adventure'),
(14, 'Fantasy'),
(16, 'Animation'),
(18, 'Drama'),
(27, 'Horror'),
(28, 'Action'),
(35, 'Comedy'),
(36, 'History'),
(37, 'Western'),
(53, 'Thriller'),
(80, 'Crime'),
(99, 'Documentary'),
(878, 'Science Fiction'),
(2883, 'Aniplex'),
(7759, 'GoHands'),
(7760, 'BROSTA TV'),
(7761, 'Mardock Scramble Production Committee'),
(9648, 'Mystery'),
(10402, 'Music'),
(10749, 'Romance'),
(10751, 'Family'),
(10752, 'War'),
(10769, 'Foreign'),
(10770, 'TV Movie'),
(11176, 'Carousel Productions'),
(11602, 'Vision View Entertainment'),
(17161, 'Odyssey Media'),
(18012, 'Pulser Productions'),
(18013, 'Rogue State'),
(23822, 'The Cartel'),
(29812, 'Telescene Film Group Productions'),
(33751, 'Sentai Filmworks');
