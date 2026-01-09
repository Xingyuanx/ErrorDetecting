# 沈永佳 - 第七周个人周报

**姓名:** 沈永佳

**本周工作总结:**

1.  **学习 Spring Boot 框架:**
    *   深入学习了 Spring Boot 的核心概念，包括自动配置、起步依赖 (Starters) 和外部化配置。
    *   完成了 Spring Boot 官方文档的 “Building a RESTful Web Service” 教程，成功构建了第一个 “Hello, World” API。
    *   研究了 Spring Data JPA 的基本用法，学习了如何定义实体 (Entity) 和仓库 (Repository)。

2.  **参与数据库设计:**
    *   与团队成员共同讨论了项目的数据库设计方案。
    *   主要负责用户模块（`users` 表）和角色权限模块（`roles` 表、`permissions` 表）的字段设计。
    *   针对用户密码的存储，提出了使用 BCrypt 加盐哈希的方案，并得到了团队的认可。

3.  **搭建项目后端框架:**
    *   使用 Spring Initializr 初始化了项目的后端 Spring Boot 工程。
    *   配置了 `pom.xml` 文件，引入了 Web、Data JPA、MySQL Driver 等核心依赖。
    *   创建了项目的基础包结构（`controller`, `service`, `repository`, `entity`），为后续开发做好了准备。

**遇到的问题与解决方案:**

*   **问题:** 在配置 `application.properties` 文件连接本地 MySQL 数据库时，遇到了时区错误（`The server time zone value 'UTC' is unrecognized`）。
*   **解决方案:** 通过查阅资料，在数据库连接 URL 中加入了 `serverTimezone=UTC` 参数，成功解决了该问题。

**下周工作计划:**

1.  **开发用户注册接口:**
    *   创建 `User` 实体和 `UserRepository`。
    *   编写 `UserService`，实现用户注册的业务逻辑，包括用户名是否重复的校验和密码加密存储。
    *   编写 `AuthController`，对外暴露 `/api/v1/auth/register` 接口。

2.  **开发用户登录接口:**
    *   在 `UserService` 中实现用户登录的业务逻辑，校验用户名和密码。
    *   学习并集成 JWT (JSON Web Tokens)，在登录成功后生成 Token 并返回给前端。
    *   在 `AuthController` 中暴露 `/api/v1/auth/login` 接口。