# Changelog

## [0.2.0](https://github.com/pockerman/qubit-notes/compare/v0.1.0...v0.2.0) (2026-10-29)


### ⚠ BREAKING CHANGES

* the environment variables are QUBIT_NOTES_* instead of STUDY_ASSISTANT_*, and the command is qubit-notes instead of study-assistant.

### Features

* a container image of the app, published to GHCR ([b9815e1](https://github.com/pockerman/qubit-notes/commit/b9815e19f60036544a73a6e03e944e426733bebe))
* a navigation menu, and admins give the app its missing keys fro… ([91f5b4e](https://github.com/pockerman/qubit-notes/commit/91f5b4eead6f1b5a4f045ac1e349d5bf3cf2b938))
* a navigation menu, and admins give the app its missing keys from the platform's status ([d1f661f](https://github.com/pockerman/qubit-notes/commit/d1f661f960105de24b06d793b380d86ec860cd3a))
* a page for each subject, with its topics; the course page lists subjects ([112852b](https://github.com/pockerman/qubit-notes/commit/112852b4ff95bf80020c397e9abbb0f53bf6e0c2))
* a page for each subject, with its topics; the course page lists… ([6a232bb](https://github.com/pockerman/qubit-notes/commit/6a232bbcdf27600a053063e47553df40b78697be))
* a page for each topic, and a course page that lists only topics ([e0240f7](https://github.com/pockerman/qubit-notes/commit/e0240f78ed53b0a65402f10f6ab21be716257c6c))
* accept uploads up to 100 MB ([93aab74](https://github.com/pockerman/qubit-notes/commit/93aab7488e787e42729fe3fc67723603db8027d9))
* add a topic to a subject, and see a course's members on their own page ([5fc4dfa](https://github.com/pockerman/qubit-notes/commit/5fc4dfa4b6a22fd45782d3af3f3ae477ea96f4db))
* add images while editing a Markdown material ([5ce69b7](https://github.com/pockerman/qubit-notes/commit/5ce69b7d38272dbd59096e30950550cf6aece3f6))
* add images while editing a Markdown material ([f0ea1de](https://github.com/pockerman/qubit-notes/commit/f0ea1de161e86a6bfcd92bb543397524488704f4))
* ask the assistant about the material, in words ([0930812](https://github.com/pockerman/qubit-notes/commit/0930812a6ccb4032fa267cbddbf42ad8eecd9327))
* change my email and password in Settings › Account; Settings ha… ([f770e4a](https://github.com/pockerman/qubit-notes/commit/f770e4a927c632625cee2df15657d9086d053c32))
* change my email and password in Settings › Account; Settings has a submenu ([91cdf06](https://github.com/pockerman/qubit-notes/commit/91cdf060c56294752c41aa8f9eef4eb2a3bab295))
* choose the AI's provider and model in Settings; default models … ([9b1355a](https://github.com/pockerman/qubit-notes/commit/9b1355aca70b82fa973cf1bab9ad9ebf3c5937f2))
* choose the AI's provider and model in Settings; default models per provider ([804931c](https://github.com/pockerman/qubit-notes/commit/804931ca4e8dfc2f24905272c7c75bd83f42eb00))
* choose the materials to generate from in a drop-down menu, with All ([0f381ed](https://github.com/pockerman/qubit-notes/commit/0f381ed4d6643c6ef57c275d6a563bd1e7172c05))
* choose the materials to generate from in a drop-down menu, with… ([1d94851](https://github.com/pockerman/qubit-notes/commit/1d9485175a84e571328de204e4525ccb64769efc))
* choose the materials to generate from in the generate view, and cancel it ([bb694d4](https://github.com/pockerman/qubit-notes/commit/bb694d400996390d0fe891cffa42349eeebcd6f7))
* cognito sign in ([e433413](https://github.com/pockerman/qubit-notes/commit/e4334132344daa2c47aff72dd1671a0732c1a9a2))
* container image ([0ed6386](https://github.com/pockerman/qubit-notes/commit/0ed6386f26f69cae20f2cf9f952c1379640676ee))
* convert documents ([5edcf74](https://github.com/pockerman/qubit-notes/commit/5edcf7408cb03042bab3f33ac014142469b4d78a))
* convert PDFs and EPUBs to Markdown that students edit ([4e808e6](https://github.com/pockerman/qubit-notes/commit/4e808e6a3b77d66eedfaee144272f784c8b60da1))
* courses shown by their titles, renameable by their creator; ren… ([d130f9e](https://github.com/pockerman/qubit-notes/commit/d130f9e14928695ee6fd1f71c2678eb090d9d4c5))
* courses shown by their titles, renameable by their creator; rename a topic from its page ([447f190](https://github.com/pockerman/qubit-notes/commit/447f190b7878c34edb504cb85612f04d6a46d83a))
* create a subject or topic on the Add material page, without a file ([5ba4ff9](https://github.com/pockerman/qubit-notes/commit/5ba4ff94ab5f9b2baad1c18505a8a4e2f8f19d1a))
* create a subject or topic on the Add material page, without a file ([52a91fc](https://github.com/pockerman/qubit-notes/commit/52a91fcae9590dfef3655bd43de1d3fd636797d2))
* create subjects before their topics, and delete empty ones ([6b45f83](https://github.com/pockerman/qubit-notes/commit/6b45f8391d596e7011a3fa970083f225ddcad4c9))
* create subjects before their topics, and delete empty ones ([1a781a5](https://github.com/pockerman/qubit-notes/commit/1a781a5d274397eab1e9090ec3aa55cbd4ede90b))
* deploy aws ([e68cb59](https://github.com/pockerman/qubit-notes/commit/e68cb598cf8f1003f4d5146b867364dc87a925e3))
* deploy the app on AWS with Terraform ([0f6e898](https://github.com/pockerman/qubit-notes/commit/0f6e8988df60774c58bdd7805e7dc015d3da3e64))
* embed material with bge-small-en-v1.5, named on every ingestion ([2daa21f](https://github.com/pockerman/qubit-notes/commit/2daa21f6c723432c9aac96e7ac41972603a875c1))
* embed material with bge-small-en-v1.5, named on every ingestion ([46a7054](https://github.com/pockerman/qubit-notes/commit/46a70547bdb1f7db14d7c7067caf681d085ec03b))
* flashcards, and reviews of them by spaced repetition ([9436903](https://github.com/pockerman/qubit-notes/commit/943690341ff4c6aa1428601b774fa6527ad69fbc))
* give the app's keys in Settings; the platform's status sends ad… ([91c925b](https://github.com/pockerman/qubit-notes/commit/91c925b33b416d4e1565ac474272461670592c6d))
* give the app's keys in Settings; the platform's status sends admins there ([9365c95](https://github.com/pockerman/qubit-notes/commit/9365c950228c4d07c98734dda6b3a66a5f033c91))
* images in Markdown material, uploaded with it, added while writ… ([696d1f9](https://github.com/pockerman/qubit-notes/commit/696d1f93ee422d3b1287f0cdca0ed4641b5d8620))
* images in Markdown material, uploaded with it, added while writing, or added when missing ([ed334f5](https://github.com/pockerman/qubit-notes/commit/ed334f592b1bd400c1a4f554ad0867735cc6cfef))
* keep a PDF's or an EPUB's lessons with it as their original ([2b6b5ef](https://github.com/pockerman/qubit-notes/commit/2b6b5ef13ffc59dffc225bfbe8542b739e286186))
* keep papers under My papers, each studied whole, apart from courses ([ccd7546](https://github.com/pockerman/qubit-notes/commit/ccd7546d43c732e121f3535cb4d96635a66ffc3e))
* keep the app's data in Postgres, with Alembic migrations ([2cad0dd](https://github.com/pockerman/qubit-notes/commit/2cad0dde75eb0edc77da69acd40a88b80457ab8e))
* keep the app's data in Postgres, with Alembic migrations ([63fe4ba](https://github.com/pockerman/qubit-notes/commit/63fe4bacfc10b285deadc291c3c3ef02e0b17c58))
* make a subject's lessons from a PDF, an EPUB or a Markdown document ([39c81d2](https://github.com/pockerman/qubit-notes/commit/39c81d205b8ea629e0cd3a81ef961dacb0c98204))
* manage courses, materials and sharing in the browser ([61e695b](https://github.com/pockerman/qubit-notes/commit/61e695bf287afb1f11a641e46553434236758caf))
* materials grouped by course, subject and topic, and shared courses ([bfb41fa](https://github.com/pockerman/qubit-notes/commit/bfb41fa2b508eacbffd713ab165d080316710dfd))
* next and previous material, and AI-generated material from a to… ([06ac598](https://github.com/pockerman/qubit-notes/commit/06ac598145e580c1fd55122daa63ac5139338b17))
* next and previous material, and AI-generated material from a topic's materials ([717017f](https://github.com/pockerman/qubit-notes/commit/717017f9a2b64d99167ef3bdeaaac703caa2af26))
* owners set the order in which a subject's topics are read ([29f0d7f](https://github.com/pockerman/qubit-notes/commit/29f0d7f48b6cbc76ec0458e23bfd194155325dd0))
* read material section by section, and download it ([35cbfce](https://github.com/pockerman/qubit-notes/commit/35cbfcebce92216459ffcaefa299bd28235d9e85))
* references between topics, materials and sections of a course ([2548974](https://github.com/pockerman/qubit-notes/commit/2548974e718fa2cf5b569ea10ba16b088e58b407))
* rename qubit notes ([c80b442](https://github.com/pockerman/qubit-notes/commit/c80b442263e8bbf2a11168dd908ef77ff1a780bc))
* report the platform's health from gogi's health service ([6dce69f](https://github.com/pockerman/qubit-notes/commit/6dce69f18b410f8f11f63498a0ef33a9ff616215))
* run as an application of gogi with its own key ([cef8217](https://github.com/pockerman/qubit-notes/commit/cef8217786c81f5ca22c1909f9bb162704cc743c))
* run on the app's own platform, with gogi optional ([5159305](https://github.com/pockerman/qubit-notes/commit/51593058a8999093c7e77a034565c4d63cb08319))
* show a subject's originals on its page, each hidden until shown ([5307d17](https://github.com/pockerman/qubit-notes/commit/5307d1716c96bbe4abe6ebba7eacac7fb3f772e4))
* sign students in with Amazon Cognito ([d526ae1](https://github.com/pockerman/qubit-notes/commit/d526ae13470748dd6187b90f0a30673945d9679c))
* standalone platform ([6cf1698](https://github.com/pockerman/qubit-notes/commit/6cf169858a6aa30c995f26f2eec6d07c1a3c8053))
* start from my courses, create courses and topics, edit material ([f1c989d](https://github.com/pockerman/qubit-notes/commit/f1c989d2eb9db8bb841a4277be22c81c88bf8269))
* subjects and topics shown by the names typed, renameable, and n… ([a22be9f](https://github.com/pockerman/qubit-notes/commit/a22be9fadcaa6718720cd3a09ad0c3042769a724))
* subjects and topics shown by the names typed, renameable, and next/previous by topic ([607cfc5](https://github.com/pockerman/qubit-notes/commit/607cfc59fdf5a4a5087a64b9e8d9d0e4c2735e80))
* summaries and quizzes of a section, a document or a topic ([b6d9b38](https://github.com/pockerman/qubit-notes/commit/b6d9b38419fd1560fe10648e26057e22fe94df48))
* take notes on passages of texts and moments of videos ([ea87d9b](https://github.com/pockerman/qubit-notes/commit/ea87d9b669b6627d045ade50a1f209d5857bd7f9))
* the creator of a course can delete it, and everything in it ([0a7e3d5](https://github.com/pockerman/qubit-notes/commit/0a7e3d511095ddcddc7dc4c4d447b734536b0b9b))
* typeset LaTeX mathematics in Markdown with KaTeX ([e6ca4b6](https://github.com/pockerman/qubit-notes/commit/e6ca4b65d1c642030c55ab2a83afb84c73b41e67))
* typeset LaTeX mathematics in Markdown with KaTeX ([336ae69](https://github.com/pockerman/qubit-notes/commit/336ae6946d665aa3cfc4e5ffd0c3bfaaa85966b2))
* write a topic's material from scratch in a Markdown editor ([c5c7f6b](https://github.com/pockerman/qubit-notes/commit/c5c7f6b18fe6f4c9f8f4d94e77c5bdda23a1fb4a))
* write a topic's material from scratch in a Markdown editor ([19f2c13](https://github.com/pockerman/qubit-notes/commit/19f2c1390dc05e4e324c046b8720aa1c5e471ac6))


### Bug fixes

* embed a document's chunks a few at a time, so a long one doesn't run the machine out of memory ([7773900](https://github.com/pockerman/qubit-notes/commit/7773900082e60da016ae9c94812f5db6d04c421c))
* hide a reader's flashcards from their reviews once they're removed from the course ([ec5ea86](https://github.com/pockerman/qubit-notes/commit/ec5ea866f2a9b3b43c267497bd85e71b7e173b4f))
* reject uploads over a size limit instead of failing with a 500 ([9a1d2fb](https://github.com/pockerman/qubit-notes/commit/9a1d2fbe6569dedadb12a3c42065fd09b6f335f3))
* show code in Markdown as written, a comment in it no heading ([d384e96](https://github.com/pockerman/qubit-notes/commit/d384e96cddc4818035ad166e876dda0e29ae863f))
* show links written in HTML, &lt;a href="..."&gt;label&lt;/a&gt;, as links ([7f41c79](https://github.com/pockerman/qubit-notes/commit/7f41c79727d365349de7950319bcb0281258c73f))
* tabs for My courses and My papers, keys shown and removable, a provider chosen per student, notes by their passage ([467f5df](https://github.com/pockerman/qubit-notes/commit/467f5df0ca4b995ddde3ebb3ddca3e1cc52da8c4))
* write course, subject and topic names the way they are stored ([87e498d](https://github.com/pockerman/qubit-notes/commit/87e498d2ba4675eaf9cf35598a833758edf9f68e))


### Performance

* load KaTeX only when a page has mathematics ([a4b4790](https://github.com/pockerman/qubit-notes/commit/a4b47904316ad4a89872f851b619ccd7a456c054))
* load KaTeX only when a page has mathematics ([93a1650](https://github.com/pockerman/qubit-notes/commit/93a1650091684b7df82535c773caba0ae4a8a5f9))


### Refactoring

* rename the app to qubit-notes ([3c647ef](https://github.com/pockerman/qubit-notes/commit/3c647ef24c9c7f90b637db2440d608026fc61add))


### Documentation

* list qubit-notes' features in the README; fold BDD into Development ([090bca2](https://github.com/pockerman/qubit-notes/commit/090bca2e97087ff28b6fe3a52ffa60a0810ab498))
