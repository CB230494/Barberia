# ---------------------------------------------
# 📋 SISTEMA DE CONTROL PARA BARBERÍA - STREAMLIT
# Pestaña 1: ✂️ Registro de Cortes
# ---------------------------------------------

import streamlit as st
import pandas as pd
import io
from datetime import date
from database import (
    insertar_corte,
    obtener_cortes,
    eliminar_corte,
    actualizar_corte
)

# -----------------------------
# 🎛️ Configuración de la app
# -----------------------------
st.set_page_config(
    page_title="Barbería - Registro de Cortes",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# 📌 Menú lateral
# -----------------------------
menu = st.sidebar.radio(
    "Selecciona una sección",
    [
        "✂️ Registro de Cortes",
        "📦 Inventario",
        "📅 Citas",
        "💵 Finanzas",
        "📊 Reporte General"
    ]
)

# ---------------------------------------------
# ✂️ PESTAÑA 1: Registro de Cortes
# ---------------------------------------------
if menu == "✂️ Registro de Cortes":
    st.title("✂️ Registro de Cortes Realizados")
    st.markdown("Agrega, consulta o elimina cortes realizados por los barberos.")

    # ---------- FORMULARIO NUEVO CORTE ----------
    st.subheader("➕ Agregar nuevo corte")

    with st.form("form_nuevo_corte"):
        col1, col2, col3 = st.columns(3)
        with col1:
            fecha = st.date_input("Fecha", value=date.today())
        with col2:
            barbero = st.text_input("Nombre del barbero")
        with col3:
            cliente = st.text_input("Nombre del cliente")

        tipo_corte = st.selectbox("Tipo de corte", ["Clásico", "Fade", "Diseño", "Barba", "Otro"])
        precio = st.number_input("Precio (₡)", min_value=0.0, step=500.0, format="%.2f")
        observacion = st.text_area("Observaciones (opcional)")
        submitted = st.form_submit_button("💾 Guardar")

        if submitted:
            if not barbero.strip() or not cliente.strip():
                st.warning("⚠️ Barbero y Cliente son campos obligatorios.")
            else:
                insertar_corte(str(fecha), barbero.strip(), cliente.strip(), tipo_corte, precio, observacion.strip())
                st.success("✅ Corte registrado correctamente")
                st.rerun()

    st.divider()

    # ---------- LISTADO DE CORTES REGISTRADOS ----------
    st.subheader("📋 Historial de cortes")

    cortes = obtener_cortes()
    if cortes:
        df = pd.DataFrame(cortes)
        df["fecha"] = pd.to_datetime(df["fecha"]).dt.strftime("%d/%m/%Y")
        df["precio"] = df["precio"].map(lambda x: round(x, 2))

        # Botón para descargar respaldo en Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name="Cortes")
        st.download_button(
            label="⬇️ Descargar respaldo en Excel",
            data=output.getvalue(),
            file_name="cortes_registrados.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # Mostrar los cortes en tarjetas editables
        for corte in cortes:
            with st.container():
                id_corte = corte["id"]
                editar = st.session_state.get(f"edit_{id_corte}", False)

                if editar:
                    st.markdown(f"### ✏️ Editando corte ID {id_corte}")
                    f = st.date_input("Fecha", value=pd.to_datetime(corte["fecha"]), key=f"fecha_{id_corte}")
                    b = st.text_input("Barbero", value=corte["barbero"], key=f"barbero_{id_corte}")
                    c = st.text_input("Cliente", value=corte["cliente"], key=f"cliente_{id_corte}")
                    t = st.selectbox("Tipo de corte", ["Clásico", "Fade", "Diseño", "Barba", "Otro"], index=0, key=f"tipo_{id_corte}")
                    p = st.number_input("Precio (₡)", value=float(corte["precio"]), step=500.0, format="%.2f", key=f"precio_{id_corte}")
                    o = st.text_area("Observación", value=corte["observacion"] or "", key=f"obs_{id_corte}")

                    col1, col2 = st.columns(2)
                    if col1.button("💾 Guardar", key=f"guardar_{id_corte}"):
                        actualizar_corte(id_corte, {
                            "fecha": str(f),
                            "barbero": b,
                            "cliente": c,
                            "tipo_corte": t,
                            "precio": p,
                            "observacion": o
                        })
                        st.session_state[f"edit_{id_corte}"] = False
                        st.success("✅ Corte actualizado")
                        st.rerun()
                    if col2.button("❌ Cancelar", key=f"cancelar_{id_corte}"):
                        st.session_state[f"edit_{id_corte}"] = False
                        st.rerun()
                else:
                    cols = st.columns([1.5, 2, 2, 2, 1.5, 3, 1, 1])
                    cols[0].markdown(f"🗓️ **{corte['fecha']}**")
                    cols[1].markdown(f"💈 **{corte['barbero']}**")
                    cols[2].markdown(f"👤 {corte['cliente']}")
                    cols[3].markdown(f"✂️ {corte['tipo_corte']}")
                    cols[4].markdown(f"💰 ₡{corte['precio']:,.2f}")
                    cols[5].markdown(f"📝 {corte['observacion'] or '—'}")
                    if cols[6].button("✏️", key=f"edit_{id_corte}"):
                        st.session_state[f"edit_{id_corte}"] = True
                        st.rerun()
                    if cols[7].button("🗑️", key=f"delete_{id_corte}"):
                        eliminar_corte(id_corte)
                        st.success("✅ Corte eliminado")
                        st.rerun()
    else:
        st.info("Aún no se han registrado cortes.")
# ---------------------------------------------
# 📦 PESTAÑA 2: Inventario
# ---------------------------------------------
elif menu == "📦 Inventario":
    from database import (
        insertar_producto,
        obtener_productos,
        actualizar_producto,
        eliminar_producto
    )

    st.title("📦 Inventario de Productos")
    st.markdown("Administra los productos disponibles y su stock.")

    # ---------- AGREGAR PRODUCTO ----------
    st.subheader("➕ Agregar nuevo producto")
    with st.form("form_nuevo_producto"):
        col1, col2 = st.columns(2)
        nombre = col1.text_input("Nombre del producto")
        precio_unitario = col2.number_input("Precio unitario (₡)", min_value=0.0, step=100.0, format="%.2f")
        descripcion = st.text_input("Descripción (opcional)")
        stock = st.number_input("Stock inicial", min_value=0, step=1)
        enviado = st.form_submit_button("💾 Guardar producto")

        if enviado:
            if not nombre.strip():
                st.warning("⚠️ El nombre del producto es obligatorio.")
            else:
                insertar_producto(nombre.strip(), descripcion.strip(), stock, precio_unitario)
                st.success("✅ Producto registrado correctamente")
                st.rerun()

    st.divider()

    # ---------- LISTADO DE PRODUCTOS ----------
    st.subheader("📋 Productos en inventario")
    productos = obtener_productos()

    if productos:
        df = pd.DataFrame(productos)
        df["precio_unitario"] = df["precio_unitario"].map(lambda x: round(x, 2))

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Productos")
        st.download_button(
            label="⬇️ Descargar inventario en Excel",
            data=output.getvalue(),
            file_name="inventario_productos.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        for producto in productos:
            id_producto = producto["id"]
            editando = st.session_state.get(f"edit_prod_{id_producto}", False)

            if editando:
                st.markdown(f"### ✏️ Editando producto ID {id_producto}")
                col1, col2 = st.columns(2)
                nombre_edit = col1.text_input("Nombre", value=producto["nombre"], key=f"nombre_{id_producto}")
                precio_edit = col2.number_input("Precio (₡)", value=float(producto["precio_unitario"]), step=100.0, format="%.2f", key=f"precio_{id_producto}")
                descripcion_edit = st.text_input("Descripción", value=producto["descripcion"] or "", key=f"desc_{id_producto}")
                stock_edit = st.number_input("Stock", value=int(producto["stock"]), step=1, key=f"stock_{id_producto}")
                col1, col2 = st.columns(2)
                if col1.button("💾 Guardar", key=f"guardar_{id_producto}"):
                    actualizar_producto(id_producto, {
                        "nombre": nombre_edit,
                        "precio_unitario": precio_edit,
                        "descripcion": descripcion_edit,
                        "stock": stock_edit
                    })
                    st.session_state[f"edit_prod_{id_producto}"] = False
                    st.success("✅ Producto actualizado")
                    st.rerun()
                if col2.button("❌ Cancelar", key=f"cancelar_{id_producto}"):
                    st.session_state[f"edit_prod_{id_producto}"] = False
                    st.rerun()
            else:
                cols = st.columns([2, 2, 2, 2, 1, 1])
                cols[0].markdown(f"📦 **{producto['nombre']}**")
                cols[1].markdown(f"🧾 {producto['descripcion'] or '—'}")
                cols[2].markdown(f"💰 ₡{producto['precio_unitario']:,.2f}")
                cols[3].markdown(f"📦 Stock: {producto['stock']}")
                if cols[4].button("✏️", key=f"edit_{id_producto}"):
                    st.session_state[f"edit_prod_{id_producto}"] = True
                    st.rerun()
                if cols[5].button("🗑️", key=f"del_{id_producto}"):
                    eliminar_producto(id_producto)
                    st.success("✅ Producto eliminado")
                    st.rerun()
    else:
        st.info("No hay productos registrados todavía.")
# ---------------------------------------------
# 📅 PESTAÑA 3: Citas
# ---------------------------------------------
elif menu == "📅 Citas":
    from database import (
        insertar_cita,
        obtener_citas,
        actualizar_cita,
        actualizar_estado_cita,
        eliminar_cita
    )
    from datetime import datetime, time

    st.title("📅 Gestión de Citas")
    st.markdown("Administra las citas agendadas por clientes.")

    # ---------- NUEVA CITA MANUAL ----------
    st.subheader("➕ Registrar nueva cita manualmente")

    with st.form("form_nueva_cita"):
        col1, col2 = st.columns(2)
        fecha = col1.date_input("Fecha de la cita", value=date.today())
        hora = col2.time_input("Hora de la cita", value=time(8, 0))
        cliente = st.text_input("Nombre del cliente")
        barbero = st.text_input("Barbero asignado")
        servicio = st.selectbox("Servicio solicitado", ["Corte", "Barba", "Corte + Barba", "Otro"])
        enviado = st.form_submit_button("💾 Registrar cita")

        if enviado:
            if not cliente or not barbero:
                st.warning("⚠️ Todos los campos son obligatorios.")
            else:
                insertar_cita(str(fecha), str(hora), cliente, barbero, servicio)
                st.success("✅ Cita registrada correctamente")
                st.rerun()

    st.divider()

    # ---------- VISUALIZAR CITA ----------
    st.subheader("📋 Citas agendadas")

    citas = obtener_citas()
    if citas:
        df = pd.DataFrame(citas)
        df["fecha"] = pd.to_datetime(df["fecha"]).dt.strftime("%d/%m/%Y")
        df["hora"] = df["hora"].str.slice(0, 5)

        # Botón descarga
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Citas")
        st.download_button(
            label="⬇️ Descargar citas en Excel",
            data=output.getvalue(),
            file_name="citas_agendadas.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        for cita in citas:
            id_cita = cita["id"]
            editando = st.session_state.get(f"edit_cita_{id_cita}", False)

            if editando:
                st.markdown(f"### ✏️ Editando cita ID {id_cita}")
                col1, col2 = st.columns(2)
                f = col1.date_input("Fecha", value=pd.to_datetime(cita["fecha"]), key=f"fecha_{id_cita}")
                h = col2.time_input("Hora", value=datetime.strptime(cita["hora"], "%H:%M:%S").time(), key=f"hora_{id_cita}")
                c = st.text_input("Cliente", value=cita["cliente_nombre"], key=f"cliente_{id_cita}")
                b = st.text_input("Barbero", value=cita["barbero"], key=f"barbero_{id_cita}")
                s = st.selectbox("Servicio", ["Corte", "Barba", "Corte + Barba", "Otro"], key=f"servicio_{id_cita}")
                estado = st.selectbox("Estado", ["pendiente", "aceptada", "rechazada"], index=["pendiente", "aceptada", "rechazada"].index(cita["estado"]), key=f"estado_{id_cita}")

                col1, col2 = st.columns(2)
                if col1.button("💾 Guardar", key=f"guardar_cita_{id_cita}"):
                    actualizar_cita(id_cita, {
                        "fecha": str(f),
                        "hora": str(h),
                        "cliente_nombre": c,
                        "barbero": b,
                        "servicio": s,
                        "estado": estado
                    })
                    st.session_state[f"edit_cita_{id_cita}"] = False
                    st.success("✅ Cita actualizada")
                    st.rerun()
                if col2.button("❌ Cancelar", key=f"cancelar_cita_{id_cita}"):
                    st.session_state[f"edit_cita_{id_cita}"] = False
                    st.rerun()
            else:
                cols = st.columns([1.5, 1, 2, 2, 2, 1.5, 1, 1])
                cols[0].markdown(f"📅 **{cita['fecha']}**")
                cols[1].markdown(f"⏰ {cita['hora'][:5]}")
                cols[2].markdown(f"👤 {cita['cliente_nombre']}")
                cols[3].markdown(f"💈 {cita['barbero']}")
                cols[4].markdown(f"✂️ {cita['servicio']}")
                cols[5].markdown(f"🟢 Estado: `{cita['estado']}`")
                if cols[6].button("✏️", key=f"edit_{id_cita}"):
                    st.session_state[f"edit_cita_{id_cita}"] = True
                    st.rerun()
                if cols[7].button("🗑️", key=f"del_{id_cita}"):
                    eliminar_cita(id_cita)
                    st.success("✅ Cita eliminada")
                    st.rerun()
    else:
        st.info("No hay citas registradas.")




