
-- --------------------------------------------------------

--
-- 表的结构 `credit`
--

CREATE TABLE `credit` (
  `credit_id` bigint(20) NOT NULL,
  `department` varchar(100) DEFAULT NULL,
  `job` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
