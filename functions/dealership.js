// https://2e35c4b8.eu-gb.apigw.appdomain.cloud/api/dealership

const Cloudant = require('@cloudant/cloudant');

async function main(params) {

    const cloudant = Cloudant({
        url: params.URL,
        plugins: { iamauth: { iamApiKey: params.API_KEY } }
    });
    
    const db = cloudant.db.use('dealerships');

    try {
        if (!params.state) {
            const doclist = await db.list({include_docs: true});

            const docs = doclist.rows.map( el => el.doc);

            return {result: docs};
        } else {

            const selector = {
                "st": {
                    "$eq": params.state
                }
            };

            const docs = await (new Promise((res, rej) => {
                db.find({ selector }, function (err, result) {
                    if (err) rej(err);

                    res(result.docs)
                });
            }));

            return {result: docs}
        }
    } catch (error) {
        return { error: error.description };
    }
}