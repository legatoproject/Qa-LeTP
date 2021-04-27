![Legato](https://legato.io/resources/img/legato_logo.png)

Qa-letp contains <A HREF="https://github.com/legatoproject/legato-af">
Legato</A> system testing scripts.

# Prerequisites
Clone <A HREF="https://github.com/legatoproject/LeTP">LeTP</A> repo. <br>
Clone Qa-Letp under LeTP/testing_target/public <br>
Follow instruction of LeTP to set up tool correctly. <br>
Setup the testing target. WP77xx, WP76xx, WP85, etc.

The following command should return the path of letp.
```
LeTP/configLeTP.sh
which letp
```

Run the full system test campaign.
```
cd LeTP/testing_target
letp run public/runtest/full_campaign.json
```
