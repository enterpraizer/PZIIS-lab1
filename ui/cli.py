"""CLI presentation layer."""

from __future__ import annotations

import logging
from getpass import getpass

from models.base import Role
from models.user import User
from repositories.article_repository import ArticleRepository
from repositories.category_repository import CategoryRepository
from repositories.database import session_scope
from repositories.question_repository import QuestionRepository
from repositories.user_repository import UserRepository
from services.admin_service import AdminService
from services.article_service import ArticleService
from services.auth_service import AuthService
from services.qa_service import QAService
from utils.exceptions import AppError

logger = logging.getLogger(__name__)


class CLI:
    """Interactive CLI user interface."""

    def run(self) -> None:
        """Start CLI loop."""
        while True:
            print("\n=== Справочная система малого бизнеса ===")
            print("1. Регистрация")
            print("2. Вход")
            print("3. Выход")
            choice = input("Выберите действие: ").strip()

            if choice == "1":
                self._register_flow()
            elif choice == "2":
                user = self._login_flow()
                if user:
                    self._authorized_menu(user)
            elif choice == "3":
                print("До свидания!")
                break
            else:
                print("Некорректный выбор.")

    def _register_flow(self) -> None:
        """Handle user registration."""
        username = input("Логин: ")
        password = getpass("Пароль: ")
        print("Роль: entrepreneur / consultant")
        role = input("Введите роль: ").strip().lower()

        with session_scope() as session:
            service = AuthService(UserRepository(session))
            try:
                user = service.register(username=username, password=password, role=role)
                print(f"Пользователь '{user.username}' успешно зарегистрирован")
            except AppError as exc:
                print(f"Ошибка: {exc}")

    def _login_flow(self) -> User | None:
        """Handle login."""
        username = input("Логин: ")
        password = getpass("Пароль: ")

        with session_scope() as session:
            service = AuthService(UserRepository(session))
            try:
                return service.login(username=username, password=password)
            except AppError as exc:
                print(f"Ошибка входа: {exc}")
                return None

    def _authorized_menu(self, user: User) -> None:
        """Role-aware menu after login."""
        while True:
            print(f"\nПользователь: {user.username} ({user.role.value})")
            print("1. Просмотр статей")
            print("2. Поиск статей")
            print("3. Фильтр статей по категории")
            print("4. Задать вопрос")
            print("5. Просмотр вопросов")
            print("6. Ответить на вопрос")
            print("7. Управление статьями")
            print("8. Админ панель")
            print("9. Выход из аккаунта")

            choice = input("Выберите действие: ").strip()

            if choice == "1":
                self._list_articles()
            elif choice == "2":
                self._search_articles()
            elif choice == "3":
                self._filter_articles_by_category()
            elif choice == "4":
                self._ask_question(user)
            elif choice == "5":
                self._list_questions()
            elif choice == "6":
                self._answer_question(user)
            elif choice == "7":
                self._manage_articles(user)
            elif choice == "8":
                self._admin_panel(user)
            elif choice == "9":
                print("Вы вышли из аккаунта")
                break
            else:
                print("Некорректный выбор.")

    def _list_articles(self) -> None:
        with session_scope() as session:
            service = ArticleService(
                article_repository=ArticleRepository(session),
                category_repository=CategoryRepository(session),
            )
            try:
                articles = service.list_articles()
                if not articles:
                    print("Статьи отсутствуют")
                    return

                for article in articles:
                    self._print_article(article)
            except AppError as exc:
                print(f"Ошибка: {exc}")

    def _search_articles(self) -> None:
        query = input("Введите поисковый запрос: ")
        with session_scope() as session:
            service = ArticleService(
                article_repository=ArticleRepository(session),
                category_repository=CategoryRepository(session),
            )
            try:
                articles = service.search_articles(query)
                if not articles:
                    print("По запросу ничего не найдено")
                    return
                for article in articles:
                    self._print_article(article)
            except AppError as exc:
                print(f"Ошибка поиска: {exc}")

    def _filter_articles_by_category(self) -> None:
        with session_scope() as session:
            service = ArticleService(
                article_repository=ArticleRepository(session),
                category_repository=CategoryRepository(session),
            )
            try:
                categories = service.list_categories()
                for category in categories:
                    print(f"{category.id}. {category.name}")
                category_id = int(input("ID категории: ").strip())
                articles = service.filter_articles_by_category(category_id)
                if not articles:
                    print("В категории нет статей")
                    return
                for article in articles:
                    self._print_article(article)
            except ValueError:
                print("ID должен быть числом")
            except AppError as exc:
                print(f"Ошибка: {exc}")

    def _ask_question(self, user: User) -> None:
        question_text = input("Введите вопрос: ")
        with session_scope() as session:
            current_user = UserRepository(session).get_by_id(user.id)
            if not current_user:
                print("Ошибка: пользователь не найден")
                return

            service = QAService(QuestionRepository(session))
            try:
                question = service.ask_question(current_user=current_user, text=question_text)
                print(f"Вопрос добавлен. ID: {question.id}")
            except AppError as exc:
                print(f"Ошибка: {exc}")

    def _list_questions(self) -> None:
        with session_scope() as session:
            service = QAService(QuestionRepository(session))
            try:
                questions = service.list_questions()
                if not questions:
                    print("Вопросы отсутствуют")
                    return

                for question in questions:
                    self._print_question(question)
            except AppError as exc:
                print(f"Ошибка: {exc}")

    def _answer_question(self, user: User) -> None:
        try:
            question_id = int(input("ID вопроса: ").strip())
        except ValueError:
            print("ID должен быть числом")
            return

        answer_text = input("Введите ответ: ")

        with session_scope() as session:
            current_user = UserRepository(session).get_by_id(user.id)
            if not current_user:
                print("Ошибка: пользователь не найден")
                return

            service = QAService(QuestionRepository(session))
            try:
                answer = service.answer_question(
                    current_user=current_user,
                    question_id=question_id,
                    text=answer_text,
                )
                print(f"Ответ добавлен. ID: {answer.id}")
            except AppError as exc:
                print(f"Ошибка: {exc}")

    def _manage_articles(self, user: User) -> None:
        if user.role not in {Role.CONSULTANT, Role.ADMIN}:
            print("Доступно только консультанту и администратору")
            return

        print("\nУправление статьями")
        print("1. Добавить статью")
        print("2. Изменить статью")
        print("3. Удалить статью")
        choice = input("Выберите действие: ").strip()

        with session_scope() as session:
            article_service = ArticleService(
                article_repository=ArticleRepository(session),
                category_repository=CategoryRepository(session),
            )
            current_user = UserRepository(session).get_by_id(user.id)
            if not current_user:
                print("Ошибка: пользователь не найден")
                return

            try:
                if choice == "1":
                    title = input("Заголовок: ")
                    content = input("Текст статьи: ")
                    categories = article_service.list_categories()
                    for category in categories:
                        print(f"{category.id}. {category.name}")
                    category_id = int(input("ID категории: ").strip())
                    article = article_service.create_article(
                        current_user=current_user,
                        title=title,
                        content=content,
                        category_id=category_id,
                    )
                    print(f"Статья создана. ID: {article.id}")
                elif choice == "2":
                    article_id = int(input("ID статьи: ").strip())
                    title = input("Новый заголовок: ")
                    content = input("Новый текст: ")
                    categories = article_service.list_categories()
                    for category in categories:
                        print(f"{category.id}. {category.name}")
                    category_id = int(input("ID категории: ").strip())
                    article = article_service.update_article(
                        current_user=current_user,
                        article_id=article_id,
                        title=title,
                        content=content,
                        category_id=category_id,
                    )
                    print(f"Статья обновлена. ID: {article.id}")
                elif choice == "3":
                    article_id = int(input("ID статьи: ").strip())
                    article_service.delete_article(current_user=current_user, article_id=article_id)
                    print("Статья удалена")
                else:
                    print("Некорректный выбор")
            except ValueError:
                print("ID должен быть числом")
            except AppError as exc:
                print(f"Ошибка: {exc}")

    def _admin_panel(self, user: User) -> None:
        if user.role != Role.ADMIN:
            print("Доступ разрешен только администратору")
            return

        print("\nАдмин панель")
        print("1. Список пользователей")
        print("2. Блокировать пользователя")
        print("3. Разблокировать пользователя")
        print("4. Удалить пользователя")
        choice = input("Выберите действие: ").strip()

        with session_scope() as session:
            admin_service = AdminService(UserRepository(session))
            current_user = UserRepository(session).get_by_id(user.id)
            if not current_user:
                print("Ошибка: пользователь не найден")
                return

            try:
                if choice == "1":
                    users = admin_service.list_users(current_user)
                    for u in users:
                        print(
                            f"ID={u.id} | login={u.username} | role={u.role.value} | "
                            f"blocked={'yes' if u.is_blocked else 'no'}"
                        )
                elif choice == "2":
                    target_id = int(input("ID пользователя: ").strip())
                    blocked = admin_service.block_user(current_user=current_user, user_id=target_id)
                    print(f"Пользователь '{blocked.username}' заблокирован")
                elif choice == "3":
                    target_id = int(input("ID пользователя: ").strip())
                    unblocked = admin_service.unblock_user(
                        current_user=current_user,
                        user_id=target_id,
                    )
                    print(f"Пользователь '{unblocked.username}' разблокирован")
                elif choice == "4":
                    target_id = int(input("ID пользователя: ").strip())
                    admin_service.delete_user(current_user=current_user, user_id=target_id)
                    print("Пользователь удален")
                else:
                    print("Некорректный выбор")
            except ValueError:
                print("ID должен быть числом")
            except AppError as exc:
                print(f"Ошибка: {exc}")

    @staticmethod
    def _print_article(article) -> None:
        created = article.created_at.strftime("%Y-%m-%d %H:%M")
        print("\n-------------------------")
        print(f"ID: {article.id}")
        print(f"Название: {article.title}")
        print(f"Категория: {article.category.name}")
        print(f"Автор: {article.author.username}")
        print(f"Создано: {created}")
        print("Текст:")
        print(article.content)

    @staticmethod
    def _print_question(question) -> None:
        created = question.created_at.strftime("%Y-%m-%d %H:%M")
        print("\n=========================")
        print(f"Вопрос ID: {question.id}")
        print(f"Автор: {question.author.username}")
        print(f"Создан: {created}")
        print(f"Текст: {question.text}")
        if not question.answers:
            print("Ответов пока нет")
            return

        for answer in question.answers:
            answer_created = answer.created_at.strftime("%Y-%m-%d %H:%M")
            print(f"  - Ответ ID {answer.id} от {answer.author.username} ({answer_created})")
            print(f"    {answer.text}")
