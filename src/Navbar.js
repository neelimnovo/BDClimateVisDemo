// A react component called Navbar that 
const Navbar = () => {
    return (
        <nav className="navbar navbar-expand-lg navbar-light bg-light">
            <a className="navbar-brand" href="#">Climate Change in Australia</a>
            <button className="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNavAltMarkup"
                aria-controls="navbarNavAltMarkup" aria-expanded="true" aria-label="Toggle navigation">
                <span className="navbar-toggler-icon"></span>
            </button>
            <div className="navbar-collapse collapse show" id="navbarNavAltMarkup">
                <div className="navbar-nav">
                    <a className="nav-item nav-link active" href="#">Home <span className="sr-only">(current)</span></a>
                    <a className="nav-item nav-link" href="#">About</a>
                    <a className="nav-item nav-link" href="#">Contact</a>
                </div>
            </div>
        </nav>
    );
}

export default Navbar;