import React from 'react';
import { Alert } from 'reactstrap';

export default class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false };
    }

    static getDerivedStateFromError(error) {
        // Update state so the next render will show the fallback UI.
        return {
            hasError: true,
            errorMessage: error.toString(),
        };
    }

    componentDidCatch(error, errorInfo) {
        // You can also log the error to an error reporting service
        // logErrorToMyService(error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            // You can render any custom fallback UI
            return <Alert color="danger">
                <h1>Something went wrong.</h1>
                <div>{this.state.errorMessage}</div>
            </Alert>;
        }

        return this.props.children;
    }
}
