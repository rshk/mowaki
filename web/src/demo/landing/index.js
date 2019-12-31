import React from 'react';
import { Link } from 'react-router-dom';
import { Container, Button } from 'reactstrap';

import { API_URL } from 'lib/apollo';

// import ICON from 'demo/img/icon.png';
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
        </Container>
    </div>;
}


function LandingContent() {
    return <Container className={styles.landingContent}>

        <div className="text-center">
            Your new project has been created.<br/>
            Refer to the links below on how to get started.
        </div>

    </Container>;
}


function LandingFooter() {
    return <Container className={styles.landingFooter}>

        <div className="text-center mb-3">
            <h2>Getting started</h2>
        </div>

        <div className={styles.itemsRow}>
            <div className={styles.item}>
                <Button tag={Link} to="/demo" color="primary" outline>
                    Demo applications
                </Button>
            </div>
            <div className={styles.item}>
                <Button tag="a" href="https://docs.mowaki.org/" color="primary" size="lg">
                    MoWAKi Documentation
                </Button>
            </div>
            <div className={styles.item}>
                <Button tag="a" href={API_URL} color="primary" outline>
                    Access GraphiQL
                </Button>
            </div>
        </div>

        {/*
            <div className="text-right">

            </div> */}

    </Container>;
}
