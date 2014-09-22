module.exports = function(grunt) {

  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),
    concat: {
      options: {
        separator: ';'
      },
      dist: {
        src: [
                '../public/static/js/lib/*.js',
                '../public/static/js/src/utils/Utils_h.js',
                '../public/static/js/src/**/*.js'
        ],
        dest: '../public/static/dist/core.js'
      },
    },
    uglify: {
      dist: {
        options: {
          banner: '/*! <%= pkg.name %> <%= grunt.template.today("dd-mm-yyyy") %> */\n',
          sourceMap: true
        },
        files: {
          '../public/static/dist/core.min.js': ['<%= concat.dist.dest %>']
        }
      },
    },
    jshint: {
      files: ['Gruntfile.js', '../public/static/js/src/**/*.js'],
      options: {
        // options here to override JSHint defaults
        globals: {
          jQuery: true,
          console: true,
          module: true,
          document: true
        }
      }
    },
    sass: {
      dist: {
        files: {
          '../public/static/dist/core.css' : '../public/static/css/main.scss'
        }
      },
    },
    watch: {
      css: {
        files: '../public/static/css/**/*.scss',
        tasks: ['sass:dist']
      },
      js: {
        files: ['<%= jshint.files %>'],
        tasks: ['jshint','concat:dist']
      }
    }
  });

  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-contrib-jshint');
  grunt.loadNpmTasks('grunt-contrib-watch');
  grunt.loadNpmTasks('grunt-contrib-concat');
  grunt.loadNpmTasks('grunt-contrib-sass');


};