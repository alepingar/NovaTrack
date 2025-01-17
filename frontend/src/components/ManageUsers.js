import React, { useEffect, useState } from "react";
import axios from "axios";
import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap-icons/font/bootstrap-icons.css";

function ManageUsers() {
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);
    const [editingUser, setEditingUser] = useState(null);
    const [newUser, setNewUser] = useState({
        name: "",
        surname: "",
        email: "",
        role: "staff",
        password: "",
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
            setShowModal(false);
            fetchUsers();
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

            const updatedUser = Object.keys(editingUser).reduce((acc, key) => {
                if (editingUser[key] !== undefined && editingUser[key] !== "") {
                    acc[key] = editingUser[key];
                }
                return acc;
            }, {});

            await axios.put(
                `http://127.0.0.1:8000/companies/users/${editingUser.id}`,
                updatedUser,
                {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                }
            );

            alert("Usuario actualizado correctamente");
            setEditingUser(null);
            fetchUsers();
        } catch (error) {
            alert("Error al actualizar el usuario");
            console.error("Error al actualizar usuario:", error.response?.data || error.message);
        }
    };

    if (loading) {
        return <div className="text-center mt-5">Cargando usuarios...</div>;
    }

    return (
        <div className="container mt-5">
            <div className="card shadow border-0">
                <div className="card-header bg-dark text-white d-flex justify-content-between align-items-center">
                    <h3 className="mb-0">Gestión de Usuarios</h3>
                    <button
                        className="btn btn-success"
                        onClick={() => setShowModal(true)}
                    >
                        <i className="bi bi-plus-circle"></i> Añadir Usuario
                    </button>
                </div>
                <div className="card-body">
                    <table className="table table-hover align-middle">
                        <thead className="table-dark">
                            <tr>
                                <th>Nombre</th>
                                <th>Apellidos</th>
                                <th>Correo Electrónico</th>
                                <th>Rol</th>
                                <th className="text-center">Acciones</th>
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
                                                type="text"
                                                className="form-control"
                                                name="surname"
                                                value={editingUser.surname}
                                                onChange={handleEditInputChange}
                                            />
                                        ) : (
                                            user.surname
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
                                    <td className="text-center">
                                        {editingUser?.id === user.id ? (
                                            <button
                                                className="btn btn-success btn-sm me-2"
                                                onClick={handleSaveEdit}
                                            >
                                                <i className="bi bi-check-circle"></i> Guardar
                                            </button>
                                        ) : (
                                            <button
                                                className="btn btn-warning btn-sm me-2"
                                                onClick={() => handleEditUser(user)}
                                            >
                                                <i className="bi bi-pencil-square"></i> Editar
                                            </button>
                                        )}
                                        <button
                                            className="btn btn-danger btn-sm"
                                            onClick={() => handleDeleteUser(user.id)}
                                        >
                                            <i className="bi bi-trash"></i> Eliminar
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {showModal && (
                <div className="modal show d-block" tabIndex="-1" role="dialog">
                    <div className="modal-dialog">
                        <div className="modal-content">
                            <div className="modal-header">
                                <h5 className="modal-title">Añadir Usuario</h5>
                                <button
                                    type="button"
                                    className="btn-close"
                                    aria-label="Close"
                                    onClick={() => setShowModal(false)}
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
                                        <label htmlFor="surname" className="form-label">Apellidos</label>
                                        <input
                                            type="text"
                                            className="form-control"
                                            id="surname"
                                            name="surname"
                                            value={newUser.surname}
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
                                    <div className="mb-3">
                                        <label htmlFor="password" className="form-label">Contraseña</label>
                                        <input
                                            type="password"
                                            className="form-control"
                                            id="password"
                                            name="password"
                                            value={newUser.password}
                                            onChange={handleInputChange}
                                            required
                                        />
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
