DROP TABLE IF EXISTS `video`;
CREATE TABLE `video`(
  `id` int unsigned AUTO_INCREMENT,
  `aid` int COMMENT '',
  `mid` int COMMENT '',
  `url` varchar(255) COMMENT '',
  `title` text COMMENT '',
  `view` int COMMENT '',
  `danmaku` int COMMENT '',
  `reply` int COMMENT '',
  `favorite` int COMMENT '',
  `coin` int COMMENT '',
  `share` int COMMENT '',
   PRIMARY KEY (`id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;
