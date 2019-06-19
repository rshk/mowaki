import React from 'react';
import {Alert} from 'reactstrap';


export default class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false };
    }

    static getDerivedStateFromError(error) {
        // Update state so the next render will show the fallback UI.
        return { hasError: true, error };
    }

    componentDidCatch(error, info) {
        // You can also log the error to an error reporting service
        // logErrorToMyService(error, info);
    }

    render() {
        if (this.state.hasError) {
            // You can render any custom fallback UI
            return <Alert color="danger">
                <h1>Something went wrong.</h1>
                {this.state.error && <div>
                    {this.state.error.toString()}
                </div>}
            </Alert>;
        }

        return this.props.children;
    }
}
