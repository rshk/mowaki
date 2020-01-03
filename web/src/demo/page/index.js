import React from 'react';
import { Link } from 'react-router-dom';
import { Container, Button } from 'reactstrap';

import { API_URL } from 'lib/apollo';

import ErrorBoundary from 'demo/error-boundary';
import LOGO from 'demo/img/mowaki.png';

import styles from './index.scss';


export default function Page({children, ...props}) {
    return <div className={styles.page}>
        <PageHeader {...props} />
        <ErrorBoundary>
            {children || ''}
        </ErrorBoundary>
    </div>;
}


function PageHeader({appTitle, appLink}) {
    return <div className={styles.pageHeader}>
        <Container>
            <div className="d-flex flex-row align-items-center">
                <Link to="/">
                    <img src={LOGO} alt="" className={styles.logo} />
                </Link>
                <Link to={appLink}>
                    <h1 className={styles.siteTitle}>
                        MoWAKi <small>{appTitle}</small>
                    </h1>
                </Link>
                <div className="flex-grow-1"></div>
                <div>
                    <Button tag="a" href={API_URL} color="light" outline>
                        GraphiQL
                    </Button>
                </div>
            </div>
        </Container>
    </div>;
}


PageHeader.defaultProps = {
    appLink: '/',
    appTitle: 'Demo App',
};
