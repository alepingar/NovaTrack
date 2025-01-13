function Login() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');

    const handleLogin = async () => {
        try {
            const response = await axios.post("http://localhost:8000/users/login", { email, password });
            alert(`Token recibido: ${response.data.access_token}`);
        } catch(error) {
            alert("Error en el inicio de sesión");
        }
    };

    return (
        <div>
            <h2> Iniciar Sesión</h2>
            <input type="email" placeholder="Correo" onChange={(e) => setEmail(e.target.value)} />
            <input type="password" placeholder="Contraseña" onChange={(e) => setPassword(e.target.value)} />
            <button onClick={handleLogin}>Login</button>
        </div>
    )
}

export default Login;