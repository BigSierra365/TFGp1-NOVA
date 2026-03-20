# NOVA: High-Performance Tech Store 🌌

![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)
![Alpine.js](https://img.shields.io/badge/Alpine.js-8BC0D0?style=for-the-badge&logo=alpine.js&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?style=for-the-badge&logo=postgresql&logoColor=white)

## 🚀 Elevator Pitch
**NOVA** es una plataforma de e-commerce de productos de terceros de alto rendimiento diseñada específicamente para el sector tecnológico avanzado (Drones, Sistemas de Energía y Dispositivos Portátiles). La solución aborda la complejidad de la venta técnica mediante un sistema de configuradores dinámicos que permiten al usuario personalizar sus compras a través de packs (*bundles*) y accesorios específicos en tiempo real, garantizando una experiencia de usuario fluida, visualmente impactante y técnicamente robusta.

---

## 🎥 Demostración (EL CORE)
Observa la fluidez de la interfaz y la lógica de negocio en acción:

<video src="https://github.com/user-attachments/assets/8420a13c-d63f-4612-8e34-68fc2c356e75" width="100%" controls></video>

---

## ⚙️ Stack Tecnológico

| Tecnología | Rol en el Proyecto |
| :--- | :--- |
| **Django 5** | Backend robusto encargado de la lógica de negocio, seguridad y ORM. |
| **PostgreSQL** | Base de datos relacional para una gestión de inventario y pedidos escalable. |
| **Tailwind CSS** | Framework de estilos para un diseño moderno, responsive y "Premium Feel". |
| **Alpine.js** | Reactividad ligera en el frontend para carruseles y actualizaciones de precio sin recarga. |

---

## ✨ Características Principales
- **Configurador Dinámico de Packs:** Selección reactiva de bundles y accesorios con actualización instantánea de precios mediante Fetch API.
- **Diseño Responsive Pro:** Interfaz adaptada minuciosamente para móviles, tablets y escritorio con estética minimalista.
- **Presentación Multimedia:** Integración de videoplayer de YouTube/Vimeo y carruseles de imágenes optimizados.
- **Carrito Persistente Inteligente:** Transición fluida del estado del carrito entre sesiones anónimas y usuarios autenticados.
- **Buscador Predictivo:** Búsqueda en tiempo real desde la barra de navegación para mejorar la conversión.

---

## 🛠️ Gestión de Contenidos (Panel Administrativo)
El sistema integra un **Backend Administrativo robusto** accesible en la ruta `/admin`. Este panel ha sido personalizado para permitir a los gestores de la tienda:
- Control total sobre el **inventario y stock** de productos técnicos.
- Creación y edición de **Packs (Bundles)** con previsualización multimedia in-situ.
- Gestión eficiente de pedidos, usuarios y perfiles, centralizando toda la operativa del e-commerce en una interfaz manual intuitiva y segura.

---

## 🧠 Arquitectura
El proyecto sigue el **Patrón MVT (Model-View-Template)** de Django, optimizando la separación de responsabilidades. La arquitectura se ha potenciado con una capa de **interactividad ligera (Alpine.js)** en el frontend, evitando la sobrecarga de frameworks pesados y garantizando tiempos de carga excepcionales mientras se mantiene una experiencia de usuario altamente reactiva y moderna.
