
--
-- 转储表的索引
--

--
-- 表的索引 `belong_to`
--
ALTER TABLE `belong_to`
  ADD PRIMARY KEY (`tmdbid`,`collection_id`),
  ADD KEY `fk_belong_to_collection` (`collection_id`);

--
-- 表的索引 `cast`
--
ALTER TABLE `cast`
  ADD PRIMARY KEY (`cast_id`);

--
-- 表的索引 `collection`
--
ALTER TABLE `collection`
  ADD PRIMARY KEY (`collection_id`);

--
-- 表的索引 `credit`
--
ALTER TABLE `credit`
  ADD PRIMARY KEY (`credit_id`);

--
-- 表的索引 `genres`
--
ALTER TABLE `genres`
  ADD PRIMARY KEY (`genres_id`);

--
-- 表的索引 `have`
--
ALTER TABLE `have`
  ADD PRIMARY KEY (`tmdbid`,`keyword_id`),
  ADD KEY `fk_have_keyword` (`keyword_id`);

--
-- 表的索引 `isa_cast`
--
ALTER TABLE `isa_cast`
  ADD PRIMARY KEY (`person_id`,`cast_id`),
  ADD KEY `fk_isa_cast_cast` (`cast_id`);

--
-- 表的索引 `isa_credit`
--
ALTER TABLE `isa_credit`
  ADD PRIMARY KEY (`person_id`,`credit_id`),
  ADD KEY `fk_isa_credit_credit` (`credit_id`);

--
-- 表的索引 `keywords`
--
ALTER TABLE `keywords`
  ADD PRIMARY KEY (`keyword_id`),
  ADD KEY `idx_keyword_name` (`keyword_name`);

--
-- 表的索引 `link_genres`
--
ALTER TABLE `link_genres`
  ADD PRIMARY KEY (`tmdbid`,`genres_id`),
  ADD KEY `fk_link_genres_genres` (`genres_id`);

--
-- 表的索引 `made_by`
--
ALTER TABLE `made_by`
  ADD PRIMARY KEY (`tmdbid`,`person_id`),
  ADD KEY `fk_made_by_person` (`person_id`);

--
-- 表的索引 `movie`
--
ALTER TABLE `movie`
  ADD PRIMARY KEY (`tmdbid`),
  ADD KEY `idx_movie_title` (`original_title`);

--
-- 表的索引 `person`
--
ALTER TABLE `person`
  ADD PRIMARY KEY (`person_id`),
  ADD KEY `idx_person_name` (`name`);

--
-- 表的索引 `produced_by`
--
ALTER TABLE `produced_by`
  ADD PRIMARY KEY (`tmdbid`,`company_id`),
  ADD KEY `fk_produced_by_company` (`company_id`);

--
-- 表的索引 `produced_in`
--
ALTER TABLE `produced_in`
  ADD PRIMARY KEY (`tmdbid`,`iso_3166_1`),
  ADD KEY `fk_produced_in_country` (`iso_3166_1`);

--
-- 表的索引 `production_companies`
--
ALTER TABLE `production_companies`
  ADD PRIMARY KEY (`company_id`),
  ADD KEY `idx_company_name` (`company_name`);

--
-- 表的索引 `production_countries`
--
ALTER TABLE `production_countries`
  ADD PRIMARY KEY (`iso_3166_1`);

--
-- 表的索引 `rate`
--
ALTER TABLE `rate`
  ADD PRIMARY KEY (`user_id`,`tmdbid`),
  ADD KEY `fk_rate_movie` (`tmdbid`);

--
-- 表的索引 `speak`
--
ALTER TABLE `speak`
  ADD PRIMARY KEY (`tmdbid`,`iso_639_1`),
  ADD KEY `fk_speak_language` (`iso_639_1`);

--
-- 表的索引 `spoken_languages`
--
ALTER TABLE `spoken_languages`
  ADD PRIMARY KEY (`iso_639_1`);

--
-- 表的索引 `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`user_id`);

--
-- 限制导出的表
--

--
-- 限制表 `belong_to`
--
ALTER TABLE `belong_to`
  ADD CONSTRAINT `fk_belong_to_collection` FOREIGN KEY (`collection_id`) REFERENCES `collection` (`collection_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_belong_to_movie` FOREIGN KEY (`tmdbid`) REFERENCES `movie` (`tmdbid`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- 限制表 `have`
--
ALTER TABLE `have`
  ADD CONSTRAINT `fk_have_keyword` FOREIGN KEY (`keyword_id`) REFERENCES `keywords` (`keyword_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_have_movie` FOREIGN KEY (`tmdbid`) REFERENCES `movie` (`tmdbid`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- 限制表 `isa_cast`
--
ALTER TABLE `isa_cast`
  ADD CONSTRAINT `fk_isa_cast_cast` FOREIGN KEY (`cast_id`) REFERENCES `cast` (`cast_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_isa_cast_person` FOREIGN KEY (`person_id`) REFERENCES `person` (`person_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- 限制表 `isa_credit`
--
ALTER TABLE `isa_credit`
  ADD CONSTRAINT `fk_isa_credit_credit` FOREIGN KEY (`credit_id`) REFERENCES `credit` (`credit_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_isa_credit_person` FOREIGN KEY (`person_id`) REFERENCES `person` (`person_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- 限制表 `link_genres`
--
ALTER TABLE `link_genres`
  ADD CONSTRAINT `fk_link_genres_genres` FOREIGN KEY (`genres_id`) REFERENCES `genres` (`genres_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_link_genres_movie` FOREIGN KEY (`tmdbid`) REFERENCES `movie` (`tmdbid`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- 限制表 `made_by`
--
ALTER TABLE `made_by`
  ADD CONSTRAINT `fk_made_by_movie` FOREIGN KEY (`tmdbid`) REFERENCES `movie` (`tmdbid`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_made_by_person` FOREIGN KEY (`person_id`) REFERENCES `person` (`person_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- 限制表 `produced_by`
--
ALTER TABLE `produced_by`
  ADD CONSTRAINT `fk_produced_by_company` FOREIGN KEY (`company_id`) REFERENCES `production_companies` (`company_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_produced_by_movie` FOREIGN KEY (`tmdbid`) REFERENCES `movie` (`tmdbid`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- 限制表 `produced_in`
--
ALTER TABLE `produced_in`
  ADD CONSTRAINT `fk_produced_in_country` FOREIGN KEY (`iso_3166_1`) REFERENCES `production_countries` (`iso_3166_1`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_produced_in_movie` FOREIGN KEY (`tmdbid`) REFERENCES `movie` (`tmdbid`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- 限制表 `rate`
--
ALTER TABLE `rate`
  ADD CONSTRAINT `fk_rate_movie` FOREIGN KEY (`tmdbid`) REFERENCES `movie` (`tmdbid`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_rate_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- 限制表 `speak`
--
ALTER TABLE `speak`
  ADD CONSTRAINT `fk_speak_language` FOREIGN KEY (`iso_639_1`) REFERENCES `spoken_languages` (`iso_639_1`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_speak_movie` FOREIGN KEY (`tmdbid`) REFERENCES `movie` (`tmdbid`) ON DELETE CASCADE ON UPDATE CASCADE;
