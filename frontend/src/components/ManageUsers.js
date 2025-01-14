import React, { useEffect, useState } from "react";
import axios from "axios";

function ManageUsers() {
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false); // Modal para añadir usuario
    const [editingUser, setEditingUser] = useState(null); // Usuario en edición
    const [newUser, setNewUser] = useState({
        name: "",
        email: "",
        role: "staff",
    });

    const fetchUsers = async () => {
        try {
            const token = localStorage.getItem("token");
            const response = await axios.get("http://127.0.0.1:8000/companies/users", {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });
            setUsers(response.data);
            setLoading(false);
        } catch (error) {
            console.error("Error al cargar usuarios:", error);
        }
    };

    useEffect(() => {
        fetchUsers();
    }, []);

    const handleInputChange = (e) => {
        setNewUser({ ...newUser, [e.target.name]: e.target.value });
    };

    const handleAddUser = async (e) => {
        e.preventDefault();
        try {
            const token = localStorage.getItem("token");
            await axios.post("http://127.0.0.1:8000/companies/users", newUser, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });
            alert("Usuario añadido correctamente");
            setShowModal(false); // Cierra el modal
            fetchUsers(); // Recarga la lista de usuarios
        } catch (error) {
            alert("Error al añadir el usuario");
            console.error("Error:", error.response?.data || error.message);
        }
    };

    const handleDeleteUser = async (userId) => {
        try {
            const token = localStorage.getItem("token");
            await axios.delete(`http://127.0.0.1:8000/companies/users/${userId}`, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });
            alert("Usuario eliminado correctamente");
            setUsers(users.filter((user) => user.id !== userId));
        } catch (error) {
            console.error("Error al eliminar usuario:", error);
        }
    };

    const handleEditUser = (user) => {
        setEditingUser(user);
    };

    const handleEditInputChange = (e) => {
        setEditingUser({ ...editingUser, [e.target.name]: e.target.value });
    };

    const handleSaveEdit = async () => {
        try {
            const token = localStorage.getItem("token");
            await axios.put(
                `http://127.0.0.1:8000/companies/users/${editingUser.id}`,
                editingUser,
                {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                }
            );
            alert("Usuario actualizado correctamente");
            setEditingUser(null);
            fetchUsers(); // Recarga la lista de usuarios
        } catch (error) {
            console.error("Error al actualizar usuario:", error);
        }
    };

    if (loading) {
        return <p>Cargando usuarios...</p>;
    }

    return (
        <div className="container mt-5">
            <div className="card shadow">
                <div className="card-header bg-primary text-white">
                    <h3>Gestión de Usuarios</h3>
                </div>
                <div className="card-body">
                    <button
                        className="btn btn-success mb-3"
                        onClick={() => setShowModal(true)} // Abre el modal
                    >
                        Añadir Usuario
                    </button>
                    <table className="table table-striped">
                        <thead>
                            <tr>
                                <th>Nombre</th>
                                <th>Correo Electrónico</th>
                                <th>Rol</th>
                                <th>Opciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            {users.map((user) => (
                                <tr key={user.id}>
                                    <td>
                                        {editingUser?.id === user.id ? (
                                            <input
                                                type="text"
                                                className="form-control"
                                                name="name"
                                                value={editingUser.name}
                                                onChange={handleEditInputChange}
                                            />
                                        ) : (
                                            user.name
                                        )}
                                    </td>
                                    <td>
                                        {editingUser?.id === user.id ? (
                                            <input
                                                type="email"
                                                className="form-control"
                                                name="email"
                                                value={editingUser.email}
                                                onChange={handleEditInputChange}
                                            />
                                        ) : (
                                            user.email
                                        )}
                                    </td>
                                    <td>{user.role}</td>
                                    <td>
                                        {editingUser?.id === user.id ? (
                                            <button
                                                className="btn btn-success btn-sm me-2"
                                                onClick={handleSaveEdit}
                                            >
                                                Guardar
                                            </button>
                                        ) : (
                                            <button
                                                className="btn btn-warning btn-sm me-2"
                                                onClick={() => handleEditUser(user)}
                                            >
                                                Editar
                                            </button>
                                        )}
                                        <button
                                            className="btn btn-danger btn-sm"
                                            onClick={() => handleDeleteUser(user.id)}
                                        >
                                            Eliminar
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Modal para añadir usuario */}
            {showModal && (
                <div className="modal show d-block" tabIndex="-1" role="dialog">
                    <div className="modal-dialog" role="document">
                        <div className="modal-content">
                            <div className="modal-header">
                                <h5 className="modal-title">Añadir Usuario</h5>
                                <button
                                    type="button"
                                    className="btn-close"
                                    aria-label="Close"
                                    onClick={() => setShowModal(false)} // Cierra el modal
                                ></button>
                            </div>
                            <div className="modal-body">
                                <form onSubmit={handleAddUser}>
                                    <div className="mb-3">
                                        <label htmlFor="name" className="form-label">Nombre</label>
                                        <input
                                            type="text"
                                            className="form-control"
                                            id="name"
                                            name="name"
                                            value={newUser.name}
                                            onChange={handleInputChange}
                                            required
                                        />
                                    </div>
                                    <div className="mb-3">
                                        <label htmlFor="email" className="form-label">Correo Electrónico</label>
                                        <input
                                            type="email"
                                            className="form-control"
                                            id="email"
                                            name="email"
                                            value={newUser.email}
                                            onChange={handleInputChange}
                                            required
                                        />
                                    </div>
                                    <div className="mb-3">
                                        <label htmlFor="role" className="form-label">Rol</label>
                                        <select
                                            className="form-select"
                                            id="role"
                                            name="role"
                                            value={newUser.role}
                                            onChange={handleInputChange}
                                            required
                                        >
                                            <option value="staff">Staff</option>
                                            <option value="manager">Manager</option>
                                        </select>
                                    </div>
                                    <button type="submit" className="btn btn-primary w-100">Guardar</button>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default ManageUsers;
