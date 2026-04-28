# Práctica Final: Gestor de Bibliotecas 📚

¡Bienvenidos a la práctica final de Programación II!

Este proyecto es un esqueleto inicial para un sistema de **Gestión de Bibliotecas**. Vuestro objetivo es transformar este código base (que intencionadamente tiene ineficiencias y partes incompletas) en una aplicación robusta, mantenible y profesional, aplicando todas las buenas prácticas vistas durante el curso.

## 🎯 Objetivo

Desarrollar un sistema completo para gestionar el catálogo y préstamos de una biblioteca. Debéis demostrar vuestra capacidad para:
1.  **Entender y Refactorizar** código existente.
2.  **Diseñar** una arquitectura desacoplada y limpia.
3.  **Implementar** soluciones técnicas avanzadas (bases de datos, APIs, interfaces gráficas).
4.  **Trabajar en equipo** utilizando metodologías ágiles.

## Tecnologías Obligatorias

*   **Python 3.10+**: Lenguaje base.
*   **SQLAlchemy 2.x**: ORM para persistencia de datos (SQLite/PostgreSQL).
*   **Pytest**: Suite de tests con una cobertura mínima del **80%**.
*   **Streamlit**: Interfaz gráfica para usuarios y bibliotecarios.
*   **Git + GitHub**: Control de versiones y flujo de trabajo colaborativo.
*   **GitHub Actions**: CI/CD básico para ejecutar tests en cada push.

## Principios SOLID (Obligatorio)

Debéis aplicar y documentar en este README cómo habéis cumplido con:
*   **SRP** (Single Responsibility Principle)
*   **OCP** (Open/Closed Principle)
*   **LSP** (Liskov Substitution Principle)
*   **ISP** (Interface Segregation Principle)
*   **DIP** (Dependency Inversion Principle)

##  Metodología: eXtreme Programming (XP)

Durante los 3 sprints de la práctica, es OBLIGATORIO:
*   **Pair Programming**: Evidenciado en los commits (`co-authored-by`).
*   **TDD (Test-Driven Development)**: Escribir tests *antes* que el código.
*   **Refactoring Continuo**: Mejorar el código sin cambiar su comportamiento externo.
*   **Integración Continua**: GitHub Actions activo.
*   **Stand-ups Diarios**: Registro en `DAILYS.md` (fecha, asistentes, qué hice, qué haré, bloqueos).

---

##  Sistema de Evaluación Incremental

El peso de la práctica es del **35%** de la nota final. La evaluación es incremental:

### 1. Aprobado (5-6) - "Funcionamiento Básico"
*   El sistema permite listar libros, crear usuarios y gestionar préstamos básicos.
*   Uso correcto de Git (commits semánticos).
*   Tests unitarios básicos definidos y pasando (usando Mocks para aislar dependencias).
*   Código limpio y organizado.

### 2. Notable (7-8) - "Nos centramos en robustez y calidad"
*   **Todo lo del Aprobado, más:**
*   **Excepciones Personalizadas**: Gestión de errores robusta y tipada.
*   **Logging**: Sistema de logs con al menos 3 niveles (INFO, WARNING, ERROR).
*   **Refactorización del Backend**: Uso de `FastAPI` con **Enrutadores (APIRouter)** para organizar los endpoints.
*   **Optimización**: "Cachear" datos en Streamlit para mejorar el rendimiento.

### 3. Sobresaliente (9) - "Aplicamos principios de Ingeniería del Software"
*   **Todo lo del Notable, más:**
*   **Decoradores**: Uso justificado de decoradores propios.
*   **Properties**: Uso de `@property` para encapsulamiento pythonico.
*   **Context Managers**: Uso de `with ...` para gestión eficiente de recursos (sesiones DB, ficheros).
*   **Generadores**: Uso de `yield` para procesar grandes volúmenes de datos de forma eficiente.

### 4. Matrícula de Honor (10)
*   **Todo lo del Sobresaliente, más alguno de:**
*   Uso de una tecnología o técnica **no vista en clase**.
    *   *Ejemplo*: Tests de Integración/Sistema (probando endpoints con `TestClient` o BD en memoria).
    *   *Ejemplo*: Despliegue en la nube.
    *   *Ejemplo*: Uso de una base de datos NoSQL auxiliar.
* Incluir un tercer contenedor donde se encuentre la base de datos
* Sustituir docker compose por manifiestos de k8s
* ...

---

## Arquitectura del Proyecto (Estado Inicial)

El esqueleto actual es intencionadamente ineficiente.

*   `fastapi/`: Contiene el servidor API. Actualmente lee de un CSV (`books.csv`) en cada petición (¡Ineficiente!).
*   `streamlit/`: Interfaz gráfica básica. Código mezclado y poco modular.
*   `data/`: Directorio donde debéis implementar vuestros modelos de datos y conexión a BD. 

### Vuestra misión
1.  **Eliminar la dependencia del CSV**: Migrar a una base de datos real usando SQLAlchemy.
2.  **Separar responsabilidades**: Que la UI no hable directamente con la BD, sino a través de Servicios/API.
3.  **Dockerizar**: Mantener/Mejorar el `docker-compose.yml` para que todo arranque con un comando.

¡Mucho ánimo y a programar! 💻🔥
