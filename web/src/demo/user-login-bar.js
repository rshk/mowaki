import React from 'react';
import { Button, Alert, Form, FormGroup, Input } from 'reactstrap';


export default class UserLoginBar extends React.Component {
    constructor(...args) {
        super(...args);
        this.state = {userName: null};
    }

    render() {
        const {userName} = this.state;
        return <div className="text-right">
            {userName ?
             <AuthenticatedUserBar
                 user={{name: userName}}
                 doLogout={this._doLogout.bind(this)} /> :
             <AnonymousUserBar
                 doLogin={this._doLogin.bind(this)} />}
        </div>;
    }

    _doLogin(userName = 'Some User') {
        this.setState({userName});
    }

    _doLogout() {
        this.setState({userName: null});
    }
}


class AnonymousUserBar extends React.Component {

    constructor(...args) {
        super(...args);
        this.state = {
            showLoginForm: false,
            errorMessage: null,
            username: '',
            password: '',
        };
    }

    render() {
        if (this.state.errorMessage) {
            return this._renderErrorMessage(this.state.errorMessage);
        }
        if (this.state.showLoginForm) {
            return this._renderLoginForm();
        }
        return <Alert color="secondary">
            <Button onClick={() => this.setState({showLoginForm: true})}>
                Log in
            </Button>
        </Alert>;
    }

    _handleSubmit(evt) {
        evt.preventDefault();

        const {doLogin} = this.props;
        const {username, password} = this.state;
        if (username === 'admin' && password === 'admin') {
            return doLogin(username);
        }
        this.setState({
            errorMessage: 'Bad username / password combination. Try "admin" / "admin".',
        });
    }

    _renderErrorMessage(errorMessage) {
        return <Alert color="danger">
            <div className="d-flex flex-row justify-content-between align-items-center">
                <div>{errorMessage}</div>
                <div>
                    <Button type="button" color="danger"
                            onClick={() => this.setState({errorMessage: null})}>
                        Try again
                    </Button>
                </div>
            </div>
        </Alert>;
    }

    _renderLoginForm() {
        const {username, password} = this.state;

        const updateUsername = evt => this.setState({username: evt.target.value});
        const updatePassword = evt => this.setState({password: evt.target.value});

        return <Alert color="secondary">
            <Form inline className="justify-content-end"
                  onSubmit={this._handleSubmit.bind(this)}>

                <FormGroup className="mb-2 mr-sm-2 mb-sm-0">
                    <Input type="text" name="username" placeholder="Username"
                           value={username} onChange={updateUsername} />
                </FormGroup>
                <FormGroup className="mb-2 mr-sm-2 mb-sm-0">
                    <Input type="password" name="password" placeholder="Password"
                           value={password} onChange={updatePassword} />
                </FormGroup>
                <Button type="submit" color="primary">
                    Log in
                </Button>{' '}
                <Button type="button" color="link"
                        onClick={() => this.setState({showLoginForm: false})}>
                    Cancel
                </Button>
            </Form>
        </Alert>;
    }
}


function AuthenticatedUserBar({user, doLogout}) {
    return <Alert color="secondary">
        <span className="text-muted">
            Logged in as
        </span>{' '}
        <span style={{fontWeight: 'bold'}}>{user.name}</span>{' '}
        <Button onClick={doLogout}>
            Log out
        </Button>
    </Alert>;
}


function UserLogoutButton() {
}


class UserLoginForm extends React.Component {
    render() {
        return <div>

        </div>;
    }
}


// export default function UserLoginBar() {
//     return <div className="text-right">
//         User info{' '}
//         <Button color="primary">Log in</Button>{' '}
//         <Button color="primary">Log out</Button>
//     </div>;
// }
