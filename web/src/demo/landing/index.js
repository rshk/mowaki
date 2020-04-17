import React from 'react';
import { Link } from 'react-router-dom';
import { Container, Button } from 'reactstrap';

import { API_URL } from 'lib/apollo';
import LOGO from 'demo/img/mowaki.png';
import styles from './index.scss';


export default function LandingPage() {
    return <div className={styles.landingPage}>
        <LandingHeader />
        <LandingContent />
        <LandingFooter />
    </div>;
}


function LandingHeader() {
    return <div className={styles.landingHeader}>
        <Container>
            <div>
                <img src={LOGO} alt="" className={styles.logo} />
            </div>
            <h1 className={styles.siteTitle}>
                Welcome to MoWAKi
            </h1>
            <div className="text-center">
                Modular Web Application Kit
            </div>
        </Container>
    </div>;
}


function LandingContent() {
    return <Container className={styles.landingContent}>

        <div className="text-center mb-3">
            Your new project has been created.<br/>
            Check the docs, or have a look at the demos.
        </div>

        <div className="d-flex flex-row justify-content-center mb-3">
            <div className="mr-3">
                <Button tag="a" href="https://docs.mowaki.org/" color="primary" size="lg">
                    MoWAKi Documentation
                </Button>
            </div>

            <div>
                <Button tag={Link} to="/demo" color="primary" size="lg" outline>
                    Demo applications
                </Button>
            </div>
        </div>

        <div className="text-center mb-3">
            <div style={{fontSize: '.8em'}}>
                <a href={API_URL}>Access GraphiQL</a>
            </div>
        </div>

    </Container>;
}


function LandingFooter() {
    return <Container className={styles.landingFooter}>

        <hr/>

        <div className="text-center mb-3 text-muted">
            Powered by <a href="https://www.mowaki.org">MoWAKi</a>
        </div>

    </Container>;
}
