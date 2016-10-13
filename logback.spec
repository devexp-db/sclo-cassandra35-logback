%{?scl:%scl_package logback}
%{!?scl:%global pkg_name %{name}}

Name:           %{?scl_prefix}logback
Version:        1.1.7
Release:        3%{?dist}
Summary:        A Java logging library
License:        LGPLv2 or EPL
URL:            http://logback.qos.ch/
Source0:        http://%{pkg_name}.qos.ch/dist/%{pkg_name}-%{version}.tar.gz

# servlet 3.1 support
Patch0:         %{pkg_name}-1.1.7-servlet.patch
# Remove deprecate methods
Patch1:         %{pkg_name}-1.1.7-jetty.patch
Patch2:         %{pkg_name}-1.1.7-tomcat.patch
# Remove groovy for scl package
Patch3:         %{pkg_name}-1.1.7-removeGroovy.patch

BuildRequires:  %{?scl_prefix_maven}maven-local
BuildRequires:  %{?scl_prefix_maven}maven-plugin-bundle
BuildRequires:  %{?scl_prefix_maven}geronimo-jms
BuildRequires:  %{?scl_prefix_maven}maven-antrun-plugin
BuildRequires:  %{?scl_prefix_java_common}log4j >= 1.2.17
BuildRequires:  %{?scl_prefix_java_common}ant-junit
BuildRequires:  %{?scl_prefix_java_common}jansi
BuildRequires:  %{?scl_prefix_java_common}javamail
BuildRequires:  %{?scl_prefix_java_common}jetty-server
BuildRequires:  %{?scl_prefix_java_common}jetty-util
BuildRequires:  %{?scl_prefix}janino
BuildRequires:  %{?scl_prefix}slf4j
BuildRequires:  mvn(org.apache.tomcat:tomcat-catalina)
BuildRequires:  mvn(org.apache.tomcat:tomcat-coyote)
# use Groovy only in non-SCL package
%{!?scl:BuildRequires:  mvn(org.codehaus.groovy:groovy-all)
BuildRequires:  mvn(org.slf4j:slf4j-ext)
BuildRequires:  mvn(org.codehaus.gmavenplus:gmavenplus-plugin)}
%{?scl:Requires: %scl_runtime}

# test deps
%if 0
BuildRequires:  mvn(com.h2database:h2:1.2.132)
BuildRequires:  mvn(dom4j:dom4j:1.6.1)
BuildRequires:  mvn(hsqldb:hsqldb:1.8.0.7)
BuildRequires:  mvn(mysql:mysql-connector-java:5.1.9)
BuildRequires:  mvn(postgresql:postgresql:8.4-701.jdbc4)
BuildRequires:  mvn(org.easytesting:fest-assert:1.2)
BuildRequires:  mvn(org.mockito:mockito-core:1.9.0)
BuildRequires:  mvn(org.slf4j:integration:1.7.16)
BuildRequires:  mvn(org.slf4j:jul-to-slf4j:1.7.16)
BuildRequires:  mvn(org.slf4j:log4j-over-slf4j:1.7.16)
BuildRequires:  mvn(org.slf4j:slf4j-api:1.7.16:test-jar)
BuildRequires:  mvn(org.slf4j:slf4j-ext:1.7.16)
BuildRequires:  mvn(com.icegreen:greenmail:1.3)
BuildRequires:  mvn(org.subethamail:subethasmtp:2.1.0)
%endif

BuildArch:     noarch

%description
Logback is intended as a successor to the popular log4j project. At present
time, logback is divided into three modules, logback-core, logback-classic
and logback-access.

The logback-core module lays the groundwork for the other two modules. The
logback-classic module can be assimilated to a significantly improved
version of log4j. Moreover, logback-classic natively implements the SLF4J
API so that you can readily switch back and forth between logback and other
logging frameworks such as log4j or java.util.logging (JUL).

The logback-access module integrates with Servlet containers, such as
Tomcat and Jetty, to provide HTTP-access log functionality. Note that you
could easily build your own module on top of logback-core.

%package javadoc
Summary:       Javadoc for %{name}

%description javadoc
API documentation for the Logback library

# don't include these two subpackages in SCL package
%{!?scl:%package access
Summary:       Logback-access module for Servlet integration

%description access
The logback-access module integrates with Servlet containers, such as Tomcat
and Jetty, to provide HTTP-access log functionality. Note that you could easily
build your own module on top of logback-core.

%package examples
Summary:       Logback Examples Module

%description examples
logback-examples module.}

%prep
%setup -q -n %{pkg_name}-%{version}
# Clean up
find . -name "*.class" -delete
find . -name "*.cmd" -delete
find . -name "*.jar" -delete

%patch0 -p1
%patch1 -p1
%patch2 -p1
# remove groovy in scl package
%{?scl:%patch3 -p1}

%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
%pom_remove_plugin :maven-source-plugin
%pom_remove_plugin :findbugs-maven-plugin
%pom_remove_plugin -r :maven-dependency-plugin
%pom_remove_plugin -r :cobertura-maven-plugin

# Clean up the documentation
sed -i 's/\r//' LICENSE.txt README.txt docs/*.* docs/*/*.* docs/*/*/*.*
sed -i 's#"apidocs#"%{_javadocdir}/%{pkg_name}#g' docs/*.html
rm -rf docs/apidocs docs/project-reports docs/testapidocs docs/project-reports.html
rm -f docs/manual/.htaccess docs/css/site.css # Zero-length file

# Force servlet 3.1 apis
%pom_change_dep -r :servlet-api javax.servlet:javax.servlet-api:3.1.0
sed -i 's#javax.servlet.*;version="2.5"#javax.servlet.*;version="3.1"#' %{pkg_name}-access/pom.xml

rm -r %{pkg_name}-*/src/test/java/*
# remove test deps
# ch.qos.logback:logback-core:test-jar
%pom_xpath_remove -r "pom:dependency[pom:type = 'test-jar']"
%pom_xpath_remove -r "pom:dependency[pom:scope = 'test']"

# bundle-test-jar
%pom_xpath_remove -r "pom:plugin[pom:artifactId = 'maven-jar-plugin']/pom:executions"

# com.oracle:ojdbc14:10.2.0.1 com.microsoft.sqlserver:sqljdbc4:2.0
%pom_xpath_remove "pom:project/pom:profiles/pom:profile[pom:id = 'host-orion']" %{pkg_name}-access
%pom_xpath_remove "pom:project/pom:profiles" %{pkg_name}-classic

%pom_xpath_remove "pom:project/pom:profiles/pom:profile[pom:id = 'javadocjar']"

# disable for now
%pom_disable_module logback-site
# disable for SCL package
%{?scl:%pom_disable_module logback-access
%pom_disable_module logback-examples}

%pom_xpath_remove "pom:build/pom:extensions"

# Use not available org.codehaus.groovy:groovy-eclipse-compiler:2.9.1-01, org.codehaus.groovy:groovy-eclipse-batch:2.3.7-01
%pom_remove_plugin :maven-compiler-plugin logback-classic
%{!?scl:%pom_add_plugin org.codehaus.gmavenplus:gmavenplus-plugin:1.5 logback-classic "
 <executions>
  <execution>
   <goals>
    <goal>generateStubs</goal>
    <goal>testGenerateStubs</goal>
    <!--goal>compile</goal>
    <goal>testCompile</goal-->
   </goals>
  </execution>
 </executions>"}

# these modules are not needed for SCL package
%{!?scl:%mvn_package ":%{pkg_name}-access" access
%mvn_package ":%{pkg_name}-examples" examples}

# remove Groovy from SCL package
%{?scl:%pom_remove_dep org.codehaus.groovy:groovy-all logback-classic
rm -f logback-classic/src/main/java/ch/qos/logback/classic/gaffer/GafferUtil.java}
%{?scl:EOF}

%build

%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
# unavailable test dep maven-scala-plugin
# slf4jJAR and org.apache.felix.main are required by logback-examples modules for maven-antrun-plugin
%mvn_build -f -- \
  -Dorg.slf4j:slf4j-api:jar=$(build-classpath slf4j/api) \
  -Dorg.apache.felix:org.apache.felix.main:jar=$(build-classpath felix/org.apache.felix.main)
%{?scl:EOF}

%install
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
%mvn_install
%{?scl:EOF}

# files installed only in non-scl package
%{!?scl:install -d -m 755 %{buildroot}%{_datadir}/%{pkg_name}/examples
cp -r %{pkg_name}-examples/pom.xml %{pkg_name}-examples/src %{buildroot}%{_datadir}/%{pkg_name}/examples}

%files -f .mfiles
%doc README.txt docs/*
%license LICENSE.txt

%files javadoc -f .mfiles-javadoc
%license LICENSE.txt

# subpackages installed only in non-scl package
%{!?scl:%files access -f .mfiles-access
%license LICENSE.txt

%files examples -f .mfiles-examples
%license LICENSE.txt
%{_datadir}/%{pkg_name}}

%changelog
* Wed Oct 12 2016 Tomas Repik <trepik@redhat.com> - 1.1.7-3
- use standard SCL macros

* Mon Sep 26 2016 Tomas Repik <trepik@redhat.com> - 1.1.7-2
- scl conversion

* Thu Jun 23 2016 gil cattaneo <puntogil@libero.it> 1.1.7-1
- update to 1.1.7

* Mon Feb 29 2016 gil cattaneo <puntogil@libero.it> 1.1.5-1
- Update to 1.1.5

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Fri Aug 07 2015 gil cattaneo <puntogil@libero.it> 1.1.3-1
- Update to 1.1.3
- Use glassfish-servlet-apis instead of tomcat-servlet-api

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.2-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Fri Mar 27 2015 gil cattaneo <puntogil@libero.it> 1.1.2-4
- add support for jetty 9.3.0

* Fri Mar 13 2015 gil cattaneo <puntogil@libero.it> 1.1.2-3
- add support for servlet 3.1

* Fri Feb 13 2015 gil cattaneo <puntogil@libero.it> 1.1.2-2
- introduce license macro

* Fri Jan 09 2015 gil cattaneo <puntogil@libero.it> 1.1.2-1
- Update to 1.1.2

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Mon Feb 24 2014 Orion Poplawski <orion@cora.nwra.com> - 1.1.1-1
- Update to 1.1.1

* Wed Jan 29 2014 gil cattaneo <puntogil@libero.it> - 1.1.0-1
- Update to 1.1.0

* Sun Aug 04 2013 gil cattaneo <puntogil@libero.it> - 1.0.13-1
- Update to 1.0.13

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.10-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Wed Jul 10 2013 gil cattaneo <puntogil@libero.it> - 1.0.10-2
- switch to XMvn
- minor changes to adapt to current guideline

* Tue Mar 19 2013 gil cattaneo <puntogil@libero.it> - 1.0.10-1
- Update to 1.0.10

* Thu Mar 14 2013 gil cattaneo <puntogil@libero.it> - 1.0.9-4
- Use Maven build
- Removed un{used,available} plugin

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.9-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Fri Dec 21 2012 Mary Ellen Foster <mefoster@gmail.com> - 1.0.9-2
- Remove F16 backward compatibility since it's EOL soon

* Sat Dec 08 2012 gil cattaneo <puntogil@libero.it> - 1.0.9-1
- Update to 1.0.9
- Preserved timestamp in pom files
- Applied changes to build against older jetty on F16, thanks to Mary Ellen F.

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.6-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Fri Jul 13 2012 Orion Poplawski <orion@nwra.com> - 1.0.6-2
- Split off access module into sub-package (bug 663198)
- Change BR/R from servlet25 to tomcat-servlet-3.0-api (bug 819552)
- Update build.xml to include jetty jars, drop setting CLASSPATH

* Wed Jul 11 2012 gil cattaneo <puntogil@libero.it> - 1.0.6-1
- Update to 1.0.6

* Tue Mar 20 2012 Mary Ellen Foster <mefoster at gmail.com> - 1.0.1-1
- Update to 1.0.1
- Prepare for re-review

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9.18-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Tue Dec  7 2010 Stanislav Ochotnicky <sochotnicky@redhat.com> - 0.9.18-5
- Make jars and javadoc versionless
- Fix pom filenames (#655813)
- Remove gcj bits
- Other packaging cleanups/fixes

* Wed Jan 13 2010 Mary Ellen Foster <mefoster at gmail.com> - 0.9.18-4
- Change (Build)Requirement from geronimo-specs to jms

* Wed Jan 13 2010 Mary Ellen Foster <mefoster at gmail.com> - 0.9.18-3
- Add some missing (Build)Requirements

* Tue Jan 12 2010 Mary Ellen Foster <mefoster at gmail.com> - 0.9.18-2
- Add maven2 BuildRequirements
- Remove requirement for specific slf4j version

* Mon Jan 11 2010 Mary Ellen Foster <mefoster at gmail.com> - 0.9.18-1
- Update to new upstream version -- many bugfixes, see
  http://qos.ch/pipermail/announce/2009/000068.html
- Include new license tag
- Add all referenced dependencies to the Requires list
- Specify which bits of tomcat are actually used, instead of requiring
  all of it
- Don't remove hsqldb from poms any more; Maven metadata has been added

* Wed Jan  6 2010 Mary Ellen Foster <mefoster at gmail.com> - 0.9.17-3
- Manually add the Maven metadata for geronimo-specs-jms

* Wed Dec  2 2009 Mary Ellen Foster <mefoster at gmail.com> - 0.9.17-2
- Use Maven build instead (with all that entails), and include POMs
- Add -examples subpackage
- Depend on javamail 1.4

* Wed Nov 18 2009 Mary Ellen Foster <mefoster at gmail.com> - 0.9.17-1
- Initial package (using build.xml from Debian)
